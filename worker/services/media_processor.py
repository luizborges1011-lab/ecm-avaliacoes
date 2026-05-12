"""
Processa o texto exportado do Digisac:
- Detecta URLs de mídia (áudio, imagem, PDF)
- Faz download e converte para texto
- Monta o relatório formatado para avaliação pela IA
"""
import re
import time
from datetime import datetime

from worker.services.digisac import baixar_midia
from worker.services.ai_service import transcrever_audio, descrever_imagem, extrair_pdf

_URL_REGEX = re.compile(
    r'https?://[^\s]+?\.(oga|ogg|mp3|wav|jpeg|jpg|png|gif|pdf)[^\s]*',
    re.IGNORECASE,
)
_MSG_REGEX = re.compile(
    r'\[(.*?),\s(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})\]:\s*([\s\S]*?)(?=\n\[|$)'
)


def _tipo_url(extensao: str) -> str:
    ext = extensao.lower()
    if ext in ("oga", "ogg", "mp3", "wav"):
        return "audio"
    if ext in ("jpeg", "jpg", "png", "gif"):
        return "imagem"
    if ext == "pdf":
        return "pdf"
    return "outro"


def _substituir_midias(texto: str) -> str:
    """Substitui cada URL de mídia no texto pelo seu conteúdo transcrito/descrito."""
    resultado = texto
    urls_encontradas = list(_URL_REGEX.finditer(texto))

    for match in urls_encontradas:
        url_completa = match.group(0).split(" - ")[0]
        extensao = match.group(1)
        tipo = _tipo_url(extensao)

        try:
            conteudo_bytes = baixar_midia(url_completa)
        except Exception as e:
            substituicao = f"[Mídia não disponível: {e}]"
            resultado = resultado.replace(match.group(0), substituicao, 1)
            continue

        if tipo == "audio":
            try:
                transcricao = transcrever_audio(conteudo_bytes, f"audio.{extensao}")
                substituicao = transcricao
                time.sleep(2)  # throttle Whisper
            except Exception as e:
                substituicao = f"[Áudio não transcrito: {e}]"
        elif tipo == "imagem":
            try:
                descricao = descrever_imagem(conteudo_bytes)
                substituicao = f"🖼️ [Imagem: {descricao}]"
            except Exception as e:
                substituicao = f"[Imagem não descrita: {e}]"
        elif tipo == "pdf":
            try:
                texto_pdf = extrair_pdf(conteudo_bytes)
                resumo = texto_pdf[:500] + "..." if len(texto_pdf) > 500 else texto_pdf
                substituicao = f"📄 [PDF: {resumo}]"
            except Exception as e:
                substituicao = f"[PDF não extraído: {e}]"
        else:
            substituicao = f"[Arquivo: {url_completa}]"

        resultado = resultado.replace(match.group(0), substituicao, 1)

    return resultado


def _extrair_campo(texto: str, regex: str) -> str:
    m = re.search(regex, texto)
    return m.group(1).strip() if m else "N/A"


def _calcular_tempo(abertura: str, fechamento: str) -> str:
    if abertura == "N/A" or fechamento == "N/A":
        return "0h 00min"
    try:
        fmt = "%d/%m/%Y %H:%M:%S"
        diff = datetime.strptime(fechamento, fmt) - datetime.strptime(abertura, fmt)
        total = int(diff.total_seconds() / 60)
        return f"{total // 60}h {total % 60:02d}min"
    except Exception:
        return "0h 00min"


def construir_relatorio(texto_exportado: str, nomes_internos: set[str] | None = None) -> dict:
    """
    Recebe o texto bruto do Digisac export e retorna:
    {
        'protocolo': str,
        'relatorio_final': str,  # texto formatado para o GPT
        'tempo_minutos': int,
    }
    """
    texto = texto_exportado.replace("\\n", "\n")

    protocolo = _extrair_campo(texto, r"Número do protocolo:\s*(\d+)")
    nome_contato = _extrair_campo(texto, r"Nome do contato:\s*(.+)")
    numero_contato = _extrair_campo(texto, r"Número do contato:\s*(\d+)")
    abertura = _extrair_campo(texto, r"Abertura:\s*(.+)")
    fechamento = _extrair_campo(texto, r"Fechamento:\s*(.+)")
    resumo = _extrair_campo(texto, r"Resumo do atendimento:\s*([^\n]+)")

    texto_processado = _substituir_midias(texto)

    mensagens = []
    for m in _MSG_REGEX.finditer(texto_processado):
        autor = m.group(1).split("(")[0].strip()
        data_hora = m.group(2)
        conteudo = m.group(3).strip()
        if conteudo and conteudo != "undefined":
            mensagens.append((autor, data_hora, conteudo))

    # Tempo = duração real da conversa (1ª → última mensagem).
    # Evita contar fila de espera, ticket aberto overnight, etc.
    tempo_minutos = 0
    tempo_str = "0h 00min"
    if len(mensagens) >= 2:
        try:
            fmt = "%d/%m/%Y %H:%M:%S"
            t_ini = datetime.strptime(mensagens[0][1], fmt)
            t_fim = datetime.strptime(mensagens[-1][1], fmt)
            tempo_minutos = max(0, int((t_fim - t_ini).total_seconds() / 60))
            tempo_str = f"{tempo_minutos // 60}h {tempo_minutos % 60:02d}min"
        except Exception:
            tempo_str = _calcular_tempo(abertura, fechamento)
            try:
                partes = tempo_str.replace("h", "").replace("min", "").split()
                tempo_minutos = int(partes[0]) * 60 + int(partes[1])
            except Exception:
                tempo_minutos = 0
    elif mensagens:
        # Apenas 1 mensagem — considera duração zero
        tempo_minutos = 0
        tempo_str = "0h 00min"
    else:
        # Sem mensagens — cai para abertura/fechamento do ticket
        tempo_str = _calcular_tempo(abertura, fechamento)
        try:
            partes = tempo_str.replace("h", "").replace("min", "").split()
            tempo_minutos = int(partes[0]) * 60 + int(partes[1])
        except Exception:
            tempo_minutos = 0

    # Atendente principal = usuário registrado no sistema com mais mensagens.
    # Usa lista positiva (nomes_internos) para evitar que clientes ou terceiros
    # sejam confundidos com atendentes quando o nome do contato não bate exato.
    from collections import Counter
    if nomes_internos:
        _contagem = Counter(
            a for a, _, _ in mensagens
            if a.lower().strip() in nomes_internos
        )
    else:
        # Fallback sem lista: exclui cliente, BOT e Sistema pela exclusão
        _excluidos = {"sistema", "bot", nome_contato.lower().strip()}
        _contagem = Counter(
            a for a, _, _ in mensagens
            if a.lower().strip() not in _excluidos
        )
    atendente_principal = _contagem.most_common(1)[0][0] if _contagem else "Não identificado"

    sep = "═" * 59
    relatorio = (
        f"╔{sep}\n"
        f"{'REGISTRO DE ATENDIMENTO':^61}\n"
        f"╚{sep}\n\n"
        f" 📋 Protocolo: {protocolo}\n"
        f" 📝 Resumo: {resumo}\n"
        f" 👤 Contato: {nome_contato}\n"
        f" 📱 Número: {numero_contato}\n"
        f" 📅 Abertura: {abertura}\n"
        f" 📅 Fechamento: {fechamento}\n"
        f" ⏱️  Tempo: {tempo_str}\n\n"
        f"╔{sep}\n"
        f"{'HISTÓRICO DA CONVERSA':^61}\n"
        f"╚{sep}\n"
    )

    for autor, data_hora, conteudo in mensagens:
        if autor == "Sistema":
            relatorio += f"\n[Sistema]: {conteudo}"
        elif autor == "BOT":
            relatorio += f"\n\n🤖 [BOT, {data_hora}]:\n{conteudo}"
        else:
            relatorio += f"\n\n💬 [{autor}, {data_hora}]:\n   {conteudo}"

    relatorio += f"\n\n╔{sep}\n{'FIM DO ATENDIMENTO':^61}\n╚{sep}"

    return {
        "protocolo": protocolo,
        "relatorio_final": relatorio,
        "tempo_minutos": tempo_minutos,
        "tempo_formatado": tempo_str,
        "atendente_principal": atendente_principal,
    }
