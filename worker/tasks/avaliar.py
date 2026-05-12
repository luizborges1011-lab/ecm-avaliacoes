"""
Pipeline principal de avaliação automática de chamados.

Fluxo:
  calcular_periodo() → buscar_chamados_fechados() → loop por chamado:
    exportar_historico() → construir_relatorio() → avaliar_conversa() → salvar_avaliacao()
"""
import re
import logging
from datetime import datetime, timedelta, timezone

from worker.services.digisac import buscar_chamados_fechados, exportar_historico
from worker.services.ai_service import avaliar_conversa
from worker.services.media_processor import construir_relatorio
from worker.services.database import (
    protocolo_ja_processado,
    salvar_avaliacao,
    adicionar_erro_fila,
    registrar_audit,
    carregar_nomes_internos,
    carregar_prompt_avaliacao,
)

logger = logging.getLogger(__name__)

BRT = timezone(timedelta(hours=-3))


def _limpar_nome_atendente(nome: str) -> str:
    """Remove anotações de múltiplos atendentes, mantendo apenas o principal.

    Ex: 'Marina Schropfer (predominante) e Thais Seratto' → 'Marina Schropfer'
        'Samanta Pertille (com participação de X e Y)'    → 'Samanta Pertille'
    """
    # Remove tudo a partir de '('
    nome = re.sub(r'\s*\(.*', '', nome)
    # Remove sufixo ' e Nome' que indica segundo atendente
    nome = re.sub(r'\s+e\s+[A-ZÁÀÃÂÉÊÍÓÔÕÚÜ]\S.*', '', nome)
    return nome.strip()


def calcular_periodo() -> tuple[datetime, datetime]:
    """Determina a janela de tempo a processar com base na hora atual (BRT)."""
    agora = datetime.now(BRT)
    hora = agora.hour

    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    ontem = hoje - timedelta(days=1)

    if 12 <= hora < 16:
        # Execução das 12h → processa 00:00–11:59 de hoje
        inicio = hoje.replace(hour=0)
        fim = hoje.replace(hour=11, minute=59, second=59)
    elif 16 <= hora < 24:
        # Execução das 16h → processa 12:00–15:59 de hoje
        inicio = hoje.replace(hour=12)
        fim = hoje.replace(hour=15, minute=59, second=59)
    else:
        # Execução das 00:01 → processa 16:00–23:59 de ontem
        inicio = ontem.replace(hour=16)
        fim = ontem.replace(hour=23, minute=59, second=59)

    return inicio, fim


def _extrair_campo_texto(texto: str, *patterns: str) -> str:
    for pattern in patterns:
        m = re.search(pattern, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Não identificado"


def _parse_nota(texto: str) -> float:
    patterns = [
        r"🏅\s*Nota Final:\s*([\d,.]+)",
        r"Nota Final:\s*([\d,.]+)",
        r"\*\*2\.\s*NOTA\*\*[\s\n]+([\d,.]+)",
        r"Nota:\s*([\d,.]+)\s*/\s*10",
        r"Nota:\s*([\d,.]+)",
    ]
    for p in patterns:
        m = re.search(p, texto, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", "."))
    return 0.0


def _nota_para_status(nota: float) -> str:
    if nota >= 8:
        return "Excelente"
    if nota >= 6:
        return "Bom"
    if nota >= 4:
        return "Regular"
    return "Crítico"


def _extrair_bloco(texto: str, cabecalho: str, proximo_cabecalho: str | None = None) -> str:
    pattern = rf"\*\*{re.escape(cabecalho)}\*\*[\s\n]*([\s\S]*?)"
    if proximo_cabecalho:
        pattern += rf"(?=\*\*{re.escape(proximo_cabecalho)}\*\*|$)"
    else:
        pattern += r"$"
    m = re.search(pattern, texto)
    if m:
        return m.group(1).strip().replace("\n", " ")
    return "Não identificado"


def processar_chamado(ticket: dict, nomes_internos: set[str] | None = None, prompt_template: str | None = None) -> bool:
    """Processa um único chamado. Retorna True se bem sucedido ou ignorado."""
    protocol = str(ticket.get("protocol", ""))
    contact_name = ticket.get("contact", {}).get("name") or ticket.get("contactName", "")

    if not protocol:
        logger.warning("Chamado sem protocolo, ignorando.")
        return False

    # Descarta chamados entre usuários internos (atendentes conversando entre si)
    if nomes_internos and contact_name and contact_name.strip().lower() in nomes_internos:
        logger.info(f"⏭️  Protocolo {protocol} ignorado — contato interno: {contact_name}")
        return True

    if protocolo_ja_processado(protocol):
        logger.info(f"Protocolo {protocol} já processado, pulando.")
        return True

    logger.info(f"Processando protocolo {protocol} — {contact_name}")

    try:
        texto_exportado = exportar_historico(protocol)
    except Exception as e:
        logger.error(f"Erro ao exportar histórico {protocol}: {e}")
        adicionar_erro_fila(protocol, f"Erro ao exportar histórico: {e}")
        return False

    try:
        relatorio_info = construir_relatorio(texto_exportado, nomes_internos=nomes_internos)
    except Exception as e:
        logger.error(f"Erro ao construir relatório {protocol}: {e}")
        adicionar_erro_fila(protocol, f"Erro ao construir relatório: {e}")
        return False

    relatorio_final = relatorio_info["relatorio_final"]
    atendente_principal = relatorio_info.get("atendente_principal", "Não identificado")

    try:
        avaliacao_texto = avaliar_conversa(relatorio_final, prompt_template=prompt_template)
    except Exception as e:
        logger.error(f"Erro na avaliação IA {protocol}: {e}")
        adicionar_erro_fila(protocol, f"Erro na avaliação IA: {e}")
        return False

    nota = _parse_nota(avaliacao_texto)

    cliente = _extrair_campo_texto(avaliacao_texto, r"Nome do cliente:\s*([^\n\r]+)")
    # Usa contagem real de mensagens; cai para o campo GPT só se não identificado
    responsavel = atendente_principal
    if responsavel == "Não identificado":
        responsavel = _extrair_campo_texto(avaliacao_texto, r"Responsável pelo atendimento:\s*([^\n\r]+)")
    # Limpa qualquer anotação do tipo "(com participação de X)" ou "e Thais Y"
    responsavel = _limpar_nome_atendente(responsavel)
    data_atendimento = _extrair_campo_texto(avaliacao_texto, r"Data do atendimento:\s*([^\n\r]+)")
    hora_inicio = _extrair_campo_texto(avaliacao_texto, r"Horário de início:\s*([^\n\r]+)")
    hora_fim = _extrair_campo_texto(avaliacao_texto, r"Horário de fim:\s*([^\n\r]+)")
    pontos_criticos = _extrair_bloco(avaliacao_texto, "3. PONTOS CRÍTICOS", "4. FEEDBACK FINAL")
    feedback_final = _extrair_bloco(avaliacao_texto, "4. FEEDBACK FINAL")

    if not cliente or cliente == "Não identificado":
        cliente = contact_name or "Não identificado"

    tempo_min = relatorio_info["tempo_minutos"]
    horas = tempo_min // 60
    minutos = tempo_min % 60
    tempo_formatado = f"{horas}:{minutos:02d}"

    dados = {
        "protocolo": protocol,
        "cliente": cliente,
        "responsavel": responsavel,
        "data_atendimento": data_atendimento,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "tempo_minutos": tempo_min,
        "tempo_formatado": tempo_formatado,
        "nota": nota,
        "status": _nota_para_status(nota),
        "pontos_criticos": pontos_criticos,
        "feedback_final": feedback_final,
        "avaliacao_ai_completa": avaliacao_texto,
        "relatorio_conversa_original": relatorio_final,
        "data_avaliacao": datetime.utcnow().isoformat(),
    }

    try:
        salvar_avaliacao(dados)
        registrar_audit(
            usuario="Sistema",
            acao="Avaliação processada",
            entidade="Avaliação",
            entidade_id=protocol,
            detalhes=f"Processamento automático via IA. Nota: {nota}",
        )
        logger.info(f"✅ Protocolo {protocol} avaliado. Nota: {nota} ({_nota_para_status(nota)})")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar avaliação {protocol}: {e}")
        adicionar_erro_fila(protocol, f"Erro ao salvar no banco: {e}")
        return False


def executar_ciclo(data_inicio: datetime | None = None, data_fim: datetime | None = None) -> dict:
    """Ponto de entrada do ciclo de avaliação."""
    if data_inicio is None or data_fim is None:
        data_inicio, data_fim = calcular_periodo()

    periodo_str = f"{data_inicio.strftime('%d/%m %H:%M')}→{data_fim.strftime('%H:%M')}"
    logger.info(f"🔄 Iniciando ciclo: {data_inicio.isoformat()} → {data_fim.isoformat()}")

    nomes_internos = carregar_nomes_internos()
    logger.info(f"🔒 {len(nomes_internos)} nomes internos carregados para filtragem.")

    prompt_template = carregar_prompt_avaliacao()
    if prompt_template:
        logger.info("📝 Prompt customizado carregado do banco.")
    else:
        logger.info("📝 Usando prompt padrão.")

    try:
        chamados = buscar_chamados_fechados(data_inicio, data_fim)
    except Exception as e:
        logger.error(f"Erro ao buscar chamados: {e}")
        return {"sucesso": 0, "erro": 1, "total": 0, "periodo": periodo_str}

    logger.info(f"📋 {len(chamados)} chamados encontrados.")

    sucesso = 0
    erro = 0
    for ticket in chamados:
        ok = processar_chamado(ticket, nomes_internos, prompt_template=prompt_template)
        if ok:
            sucesso += 1
        else:
            erro += 1

    logger.info(f"✅ Ciclo concluído: {sucesso} processados, {erro} erros.")
    return {"sucesso": sucesso, "erro": erro, "total": len(chamados), "periodo": periodo_str}
