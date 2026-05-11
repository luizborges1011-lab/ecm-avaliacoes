import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import ErroItem


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
            rx.heading("37", size="8", color="#0F172A"),
            rx.text("atendimentos avaliados", size="1", color="#94A3B8"),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #E2E8F0",
        ),
        columns="3",
        gap="5",
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
        errors_section(),
        direction="column",
        gap="6",
        width="100%",
    )


@rx.page(route="/automacao", title="Automação — ECM", on_load=AppState.carregar_dados)
def automacao() -> rx.Component:
    return page_layout(automacao_content(), "Central de Monitoramento")
