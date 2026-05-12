import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import ErroItem, CicloLogItem


def status_card() -> rx.Component:
    return rx.grid(
        rx.card(
            rx.flex(
                rx.flex(
                    rx.icon("activity", size=20, color="#22C55E"),
                    rx.text("Status da Automação", size="2", color="#1E293B"),
                    align="center", gap="2",
                ),
                rx.badge(AppState.status_automacao, color_scheme="green", variant="soft", size="2"),
                justify="between", align="center", margin_bottom="3",
            ),
            rx.flex(
                rx.flex(
                    rx.text("Último processamento", size="1", color="#64748B"),
                    rx.text(AppState.ultimo_processamento, size="2", weight="medium", color="#1E293B"),
                    direction="column", gap="0",
                ),
                rx.flex(
                    rx.text("Próximo processamento", size="1", color="#64748B"),
                    rx.text(AppState.proximo_processamento, size="2", weight="medium", color="#7700FF"),
                    direction="column", gap="0",
                ),
                gap="8",
            ),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #E2E8F0",
        ),
        rx.card(
            rx.flex(
                rx.icon("clock", size=20, color="#7700FF"),
                rx.text("Janelas de Processamento", size="2", color="#1E293B"),
                align="center", gap="2", margin_bottom="3",
            ),
            rx.flex(
                rx.flex(
                    rx.badge("Período 1", color_scheme="violet", variant="soft"),
                    rx.text("00:00 → 11:59 (exec. 12:00)", size="2", color="#374151"),
                    align="center", gap="3", padding="8px 0", border_bottom="1px solid #F1F5F9",
                ),
                rx.flex(
                    rx.badge("Período 2", color_scheme="violet", variant="soft"),
                    rx.text("12:00 → 15:59 (exec. 16:00)", size="2", color="#374151"),
                    align="center", gap="3", padding="8px 0", border_bottom="1px solid #F1F5F9",
                ),
                rx.flex(
                    rx.badge("Período 3", color_scheme="violet", variant="soft"),
                    rx.text("16:00 → 23:59 (exec. 00:01)", size="2", color="#374151"),
                    align="center", gap="3", padding="8px 0",
                ),
                direction="column", gap="0",
            ),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #E2E8F0",
        ),
        rx.card(
            rx.flex(
                rx.icon("circle-check", size=20, color="#22C55E"),
                rx.text("Processados Hoje", size="2", color="#1E293B"),
                align="center", gap="2", margin_bottom="3",
            ),
            rx.heading(AppState.processados_hoje.to_string(), size="8", color="#0F172A"),
            rx.text("atendimentos avaliados hoje", size="1", color="#94A3B8"),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #E2E8F0",
        ),
        columns="3",
        gap="5",
    )


def trigger_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.icon("zap", size=18, color="#7700FF"),
                    rx.heading("Execução Manual", size="3", color="#1E293B"),
                    align="center", gap="2",
                ),
                rx.text(
                    "Força a execução imediata do ciclo de avaliação para o período atual.",
                    size="1", color="#94A3B8",
                ),
                direction="column", gap="1",
            ),
            rx.flex(
                rx.flex(
                    rx.icon("clock", size=13, color="#7700FF"),
                    rx.text("Período atual:", size="1", color="#64748B", weight="medium"),
                    rx.text(AppState.periodo_atual_descricao, size="1", color="#374151"),
                    align="center", gap="2",
                ),
                rx.cond(
                    AppState.ciclo_rodando,
                    rx.button(
                        rx.spinner(size="2"),
                        "Processando...",
                        disabled=True,
                        size="2",
                        color_scheme="violet",
                        variant="soft",
                    ),
                    rx.button(
                        rx.icon("play", size=14),
                        "Executar Ciclo Agora",
                        size="2",
                        color_scheme="violet",
                        on_click=AppState.rodar_ciclo_manual,
                        style={
                            "cursor": "pointer",
                            "_hover": {"opacity": "0.85"},
                        },
                    ),
                ),
                align="center",
                gap="4",
                flex_wrap="wrap",
            ),
            justify="between",
            align="center",
            flex_wrap="wrap",
            gap="4",
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #E2E8F0",
    )


def ciclo_status_badge(item: CicloLogItem) -> rx.Component:
    return rx.cond(
        item.status == "Sucesso",
        rx.badge(
            rx.flex(rx.icon("circle-check", size=11), item.status, align="center", gap="1"),
            color_scheme="green", variant="soft", size="1",
        ),
        rx.cond(
            item.status == "Com erros",
            rx.badge(
                rx.flex(rx.icon("triangle-alert", size=11), item.status, align="center", gap="1"),
                color_scheme="orange", variant="soft", size="1",
            ),
            rx.cond(
                item.status == "Falhou",
                rx.badge(
                    rx.flex(rx.icon("x-circle", size=11), item.status, align="center", gap="1"),
                    color_scheme="red", variant="soft", size="1",
                ),
                rx.badge(item.status, color_scheme="gray", variant="soft", size="1"),
            ),
        ),
    )


def ciclo_tipo_badge(item: CicloLogItem) -> rx.Component:
    return rx.cond(
        item.tipo == "manual",
        rx.badge(
            rx.flex(rx.icon("user", size=10), "Manual", align="center", gap="1"),
            color_scheme="violet", variant="soft", size="1",
        ),
        rx.badge(
            rx.flex(rx.icon("bot", size=10), "Auto", align="center", gap="1"),
            color_scheme="blue", variant="soft", size="1",
        ),
    )


def ciclo_row(item: CicloLogItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.text(item.data_hora[:16].replace("T", " "), size="1", color="#374151", font_family="monospace"),
        ),
        rx.table.cell(ciclo_tipo_badge(item)),
        rx.table.cell(
            rx.text(item.periodo, size="1", color="#64748B", font_family="monospace"),
        ),
        rx.table.cell(
            rx.text(item.total.to_string(), size="2", weight="medium", color="#1E293B", text_align="center"),
            text_align="center",
        ),
        rx.table.cell(
            rx.text(item.sucesso.to_string(), size="2", weight="medium", color="#22C55E", text_align="center"),
            text_align="center",
        ),
        rx.table.cell(
            rx.text(item.erros.to_string(), size="2", weight="medium", color="#EF4444", text_align="center"),
            text_align="center",
        ),
        rx.table.cell(ciclo_status_badge(item)),
        style={"_hover": {"background_color": "#F8FAFC"}},
    )


def ciclos_historico_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("history", size=18, color="#7700FF"),
                rx.heading("Histórico de Execuções", size="3", color="#1E293B"),
                align="center", gap="2",
            ),
            rx.text("Últimas 20 execuções do ciclo de avaliação", size="1", color="#94A3B8"),
            justify="between", align="center", margin_bottom="4",
        ),
        rx.cond(
            AppState.ciclos_log.length() == 0,
            rx.flex(
                rx.icon("inbox", size=32, color="#CBD5E1"),
                rx.text("Nenhuma execução registrada ainda", size="2", color="#94A3B8"),
                direction="column", align="center", gap="2", padding="32px",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Data/Hora"),
                        rx.table.column_header_cell("Tipo"),
                        rx.table.column_header_cell("Período"),
                        rx.table.column_header_cell(
                            rx.flex(rx.icon("hash", size=12, color="#64748B"), "Chamados", align="center", gap="1"),
                            text_align="center",
                        ),
                        rx.table.column_header_cell(
                            rx.flex(rx.icon("circle-check", size=12, color="#22C55E"), "Avaliados", align="center", gap="1"),
                            text_align="center",
                        ),
                        rx.table.column_header_cell(
                            rx.flex(rx.icon("x-circle", size=12, color="#EF4444"), "Erros", align="center", gap="1"),
                            text_align="center",
                        ),
                        rx.table.column_header_cell("Status"),
                        style={"background_color": "#F8FAFC"},
                    ),
                ),
                rx.table.body(rx.foreach(AppState.ciclos_log, ciclo_row)),
                width="100%",
                variant="ghost",
            ),
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #E2E8F0",
    )


def error_row(erro: ErroItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(erro.protocolo, size="2", font_family="monospace", color="#374151")),
        rx.table.cell(rx.text(erro.erro, size="2", color="#64748B")),
        rx.table.cell(rx.badge(erro.tentativas, "x", color_scheme="orange", variant="soft")),
        rx.table.cell(rx.text(erro.criado_em, size="1", color="#94A3B8")),
        rx.table.cell(
            rx.button(
                rx.icon("refresh-cw", size=13), "Re-processar",
                size="1", variant="outline", color_scheme="violet",
                on_click=AppState.reprocessar_erro(erro.id),
            )
        ),
        style={"_hover": {"background_color": "#FFF7ED"}},
    )


def errors_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("triangle-alert", size=18, color="#F59E0B"),
                rx.heading("Fila de Erros", size="3", color="#1E293B"),
                align="center", gap="2",
            ),
            rx.text("Atendimentos que falharam no processamento", size="1", color="#94A3B8"),
            justify="between", align="center", margin_bottom="4",
        ),
        rx.cond(
            AppState.erros_fila.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Protocolo"),
                        rx.table.column_header_cell("Erro"),
                        rx.table.column_header_cell("Tentativas"),
                        rx.table.column_header_cell("Data"),
                        rx.table.column_header_cell("Ação"),
                    ),
                    background_color="#F8FAFC",
                ),
                rx.table.body(rx.foreach(AppState.erros_fila, error_row)),
                width="100%", variant="ghost",
            ),
            rx.flex(
                rx.icon("circle-check", size=32, color="#22C55E"),
                rx.text("Nenhum erro na fila", size="3", color="#64748B"),
                direction="column", align="center", gap="2", padding="32px",
            ),
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #E2E8F0",
    )


def automacao_content() -> rx.Component:
    return rx.flex(
        status_card(),
        trigger_section(),
        ciclos_historico_section(),
        errors_section(),
        direction="column",
        gap="6",
        width="100%",
    )


@rx.page(route="/automacao", title="Automação — ECM", on_load=AppState.verificar_auth_admin)
def automacao() -> rx.Component:
    return page_layout(automacao_content(), "Central de Monitoramento")
