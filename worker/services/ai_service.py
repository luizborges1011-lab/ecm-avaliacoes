import io
import os
import time
import httpx
from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def transcrever_audio(audio_bytes: bytes, filename: str = "audio.ogg") -> str:
    client = _get_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="pt",
    )
    time.sleep(1)  # evita rate limit da OpenAI
    return result.text


def descrever_imagem(image_bytes: bytes) -> str:
    import base64
    client = _get_client()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Descreva todo o conteudo da imagem. Responda sem acento, sem hifens"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        max_tokens=300,
    )
    return resp.choices[0].message.content or ""


def extrair_pdf(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        return "[PDF: conteúdo não extraído — instale pypdf]"
    except Exception as e:
        return f"[PDF: erro ao extrair — {e}]"


PROMPT_AVALIACAO = """Você é o Auditor Sênior do Escritório Contábil Madruga (ECM). Avalie os atendimentos com base na transcrição abaixo, seguindo estritamente o algoritmo e entregando a análise final no formato especificado.

Use a transcrição como base da avaliação:
{relatorio}

=== FORMATO DE RESPOSTA ===
**1. DADOS DO ATENDIMENTO**
- Dados do Atendimento
- Nota Final (obrigatório, agora de 0 a 10)
- Pontos Críticos
- Feedback Final

**2. NOTA**
[de 0 a 10, com base no cálculo abaixo]

**3. PONTOS CRÍTICOS**
[Texto direto, técnico, sem suavizações. Aponte falhas com clareza.]

**4. FEEDBACK FINAL**
[Texto curto e com linguagem de cliente. Deve conter crítica e sugestão prática.]

=== CÁLCULO DA NOTA FINAL ===
Critérios:
- Resolutividade (peso 3.5)
- Clareza técnica (peso 3.0)
- Encerramento (peso 1.5)
- Agilidade e Cordialidade (peso 2.0)

Fórmula:
Nota Final = ((Resolutividade × 3.5) + (Clareza × 3.0) + (Encerramento × 1.5) + (Agilidade × 2.0)) ÷ 10

Exibir no formato:
🏅 Nota Final: X,XX / 10

=== REGRAS DE AVALIAÇÃO ===
🔎 Identificação do Responsável
Se houver qualquer um dos seguintes nomes no texto, este será considerado o responsável pelo atendimento (mesmo que o campo de identificação esteja ausente): Airon Capra, Alesson Biezus, Ana Cristina Pinge, Bruna Madruga, Danieli Kupper, Edson da Silva, Franciele Favero, Giulia Detoni, Greicy Pedroso, Igo Gibikoski, Joaquin Menegatti, Jessica Westarb, Luana Ribeiro, Luiz Gambim, Luiz Henrique Borges, Marcelo A. Domeraska, Maria Clara Borges, Mariana Ravana, Marina Schropfer, Mauricio Vieira, Naiara Dalmora, Rozane Chaves, Samanta Pertille, Simone Chenet, Thais Seratto, Victoria Baumgardt, William Madruga.
- Se mais de um aparecer, usar o que mais se repete.
- Se nenhum aparecer, usar: "Não identificado"

1. Avalie somente a atuação do atendente do ECM.
- Ignore falas de terceiros (bancos, clientes, cartórios, etc.).
- Se uma explicação técnica veio do terceiro, NÃO atribua ao ECM.
- Se a solução depende de terceiros e o ECM informou isso claramente, NÃO penalize.

2. Agilidade:
- Avalie apenas o tempo de resposta do ECM.
- Desconsidere demoras causadas por terceiros.

HORÁRIOS, FINS DE SEMANA E FERIADOS
Primeira mensagem do cliente após 17h30 → ECM deve responder até 09h00 do próximo dia útil.
Mensagem do cliente após 12h00 → prazo até 14h00 do mesmo dia útil.
Não contabilizar tempo fora do horário comercial (se for a primeira mensagem iniciada fora do horário)
Fim de semana pausa contagem: sábado 00h00 → segunda 09h00.
Feriados pausam até 09h00 do próximo útil.

3. Clareza:
- A mensagem do ECM deve ser objetiva e compreensível.
- Quando a explicação estiver ausente, oriente melhoria, mas sem aplicar nota baixa injustificadamente.
- Só aplique nota baixa em Clareza quando a falta de explicação comprometer diretamente a compreensão do cliente em atendimentos com troca ativa.
- Em mensagens únicas, a clareza é importante, mas deve ser ponderada. Se a intenção foi clara, mas o conteúdo estava incompleto, aplique nota intermediária.

4. Encerramento:
- Se o atendimento foi iniciado pelo ECM para solicitar algo, não é necessário exigir mensagem formal de encerramento.
- Um agradecimento simples e cordial como "fico à disposição" é suficiente.
- Para atendimentos iniciados pelo cliente, mantenha o padrão: mensagem de encerramento com clareza, oferecendo apoio final.
- Se o cliente não respondeu e o ECM enviou uma mensagem válida, também não é necessário encerrar formalmente.
- Se constar algo como resolveu por chamada, considere como resolvido e não penalize.
- Para atendimentos com troca de mensagens (interação mútua), espere uma mensagem de encerramento clara.
- Nunca penalize encerramento quando o cliente não respondeu e o ECM cumpriu sua parte com uma solicitação clara e educada.

5. Mensagens automáticas:
- Em comunicados simples, avalie clareza e tom.
- Não exija interação ou encerramento.
- Tempo total do chamado não impacta a nota se não houve resposta do cliente.

=== ERROS QUE DEVEM SER EVITADOS ===
- ❌ Não atribuir falas técnicas de terceiros ao ECM.
- ❌ Não penalizar o ECM por ausência de resolução quando o problema é externo.
- ❌ Não usar o tempo total do atendimento como critério se a demora não foi causada pelo ECM.
- ❌ Não exigir iniciativas fora da responsabilidade do ECM.
- ✅ Reforce a importância de um tom profissional.
- ✅ Aponte informalidade, falta de clareza ou omissão de orientações quando aplicável.
- ✅ Sugira formas de melhoria realistas, dentro do controle do atendente.

📴 Atendimentos encerrados por inatividade do cliente
- Se o atendimento foi iniciado corretamente pelo ECM (com saudação e solicitação clara), e o cliente não respondeu, não penalize com nota baixa.
- Nesses casos, avalie apenas o conteúdo da mensagem inicial.
- Uma única mensagem insuficiente pode receber nota intermediária (ex: 7,0 a 8,0), se o erro for apenas falta de clareza.
- Só aplique notas abaixo de 5 se houver também falhas de conduta, desinteresse, grosseria ou erro técnico grave.

📨 Atendimentos iniciados pelo ECM junto a terceiros
- Quando o colaborador do ECM iniciar o contato com um terceiro externo, e não houver resposta do interlocutor, não penalizar por encerramento breve.
- Nesses casos, avalie se a solicitação inicial foi clara e completa.
- Penalize apenas se a mensagem estiver vaga ou genérica demais.
- Não penalize o tempo de atendimento se o terceiro não respondeu.

📝 Retornos de clientes
Se o atendimento for um caso em que o cliente enviou apenas uma mensagem curta, educada ou irrelevante (ex.: 'obrigado', 'ok', 'valeu', emojis), especialmente quando se trata da resposta a um chamado já encerrado, NÃO considere isso como um atendimento ruim. O fechamento rápido é considerado adequado. Atribua nota máxima e registre que o chamado foi encerrado corretamente por ausência de necessidade de suporte.

=== TOM DA AVALIAÇÃO ===
Direto, técnico, crítico, focado em melhoria contínua. Evite julgamentos genéricos ou injustos.

Avalie o atendimento e retorne EXATAMENTE neste formato:

**1. DADOS DO ATENDIMENTO**
- Nome do cliente: [extrair do relatório]
- Responsável pelo atendimento: [nome identificado]
- Data do atendimento: [extrair do relatório]
- Horário de início: [extrair do relatório]
- Horário de fim: [extrair do relatório]
- Tempo total: [calcular em minutos]

**2. NOTA**
[número de 0 a 10]

**3. PONTOS CRÍTICOS**
[texto direto]

**4. FEEDBACK FINAL**
[texto curto]"""


def avaliar_conversa(relatorio: str) -> str:
    client = _get_client()
    prompt = PROMPT_AVALIACAO.format(relatorio=relatorio)
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content or ""
