import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AvaliacaoItem


def nota_color(nota: float) -> rx.Var:
    return rx.cond(nota >= 8, "#22C55E", rx.cond(nota >= 6, "#7700FF", rx.cond(nota >= 4, "#F59E0B", "#EF4444")))


def table_row(av: AvaliacaoItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.text(av.protocolo, size="1", color="#64748B", font_family="monospace"),
                rx.text(av.data_atendimento, size="1", color="#94A3B8"),
                direction="column",
                gap="0",
            )
        ),
        rx.table.cell(rx.text(av.cliente, size="2", weight="medium", color="#1E293B")),
        rx.table.cell(
            rx.flex(
                rx.avatar(fallback=av.responsavel[:2], size="1", color_scheme="violet"),
                rx.text(av.responsavel, size="2", color="#374151"),
                align="center",
                gap="2",
            )
        ),
        rx.table.cell(
            rx.flex(
                rx.text(av.nota, size="2", color=nota_color(av.nota)),
                rx.text("/10", size="1", color="#94A3B8"),
                align="baseline",
                gap="1",
            )
        ),
        rx.table.cell(
            rx.match(
                av.status,
                ("Excelente", rx.badge("Excelente", color_scheme="green", variant="soft")),
                ("Bom", rx.badge("Bom", color_scheme="violet", variant="soft")),
                ("Regular", rx.badge("Regular", color_scheme="orange", variant="soft")),
                ("Crítico", rx.badge("Crítico", color_scheme="red", variant="soft")),
                rx.badge(av.status, variant="soft"),
            )
        ),
        rx.table.cell(rx.text(av.tempo_formatado, size="2", color="#64748B")),
        rx.table.cell(
            rx.match(
                av.kanban_status,
                ("Pendente", rx.badge("Pendente", color_scheme="gray", variant="outline")),
                ("Análise Humana", rx.badge("Análise Humana", color_scheme="orange", variant="outline")),
                ("Feedback", rx.badge("Feedback", color_scheme="purple", variant="outline")),
                ("Concluído Com Ressalvas", rx.badge("C/ Ressalvas", color_scheme="yellow", variant="soft")),
                ("Concluído Sem Ressalvas", rx.badge("Concluído", color_scheme="green", variant="soft")),
                rx.badge(av.kanban_status, variant="outline"),
            )
        ),
        rx.table.cell(
            rx.icon_button(
                rx.icon("eye", size=15),
                variant="ghost",
                color_scheme="violet",
                size="1",
                on_click=AppState.open_avaliacao(av.id),
            )
        ),
        style={"_hover": {"background_color": "#F8FAFC"}, "cursor": "pointer"},
        on_click=AppState.open_avaliacao(av.id),
    )


def filters_bar() -> rx.Component:
    return rx.flex(
        rx.input(
            rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
            placeholder="Buscar protocolo, cliente ou atendente...",
            value=AppState.search_query,
            on_change=AppState.set_search,
            width="320px",
            style={"background_color": "white"},
        ),
        rx.select(
            ["Excelente", "Bom", "Regular", "Crítico"],
            placeholder="Status",
            value=AppState.filter_status,
            on_change=AppState.set_filter_status,
            width="160px",
        ),
        rx.select(
            AppState.atendentes_nomes,
            placeholder="Atendente",
            value=AppState.filter_responsavel,
            on_change=AppState.set_filter_responsavel,
            width="220px",
        ),
        rx.button(
            rx.icon("x", size=14), "Limpar",
            variant="ghost", color_scheme="gray", size="2",
            on_click=AppState.clear_filters,
        ),
        rx.flex(flex="1"),
        rx.button(
            rx.icon("download", size=14), "Exportar CSV",
            variant="outline", color_scheme="violet", size="2",
        ),
        align="center",
        gap="3",
        padding="16px 0",
        flex_wrap="wrap",
    )


def avaliacao_drawer() -> rx.Component:
    av = AppState.selected_avaliacao
    return rx.drawer.root(
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.flex(
                    rx.flex(
                        rx.flex(
                            rx.heading("Detalhes da Avaliação", size="4", color="#1E293B"),
                            rx.text(av.protocolo, size="1", color="#94A3B8", font_family="monospace"),
                            direction="column", gap="1",
                        ),
                        rx.icon_button(
                            rx.icon("x", size=18), variant="ghost", color_scheme="gray",
                            on_click=AppState.close_drawer,
                        ),
                        justify="between", align="start",
                        padding="20px 24px",
                        border_bottom="1px solid #E2E8F0",
                    ),
                    rx.flex(
                        rx.grid(
                            rx.flex(
                                rx.text("Cliente", size="1", color="#64748B", weight="medium"),
                                rx.text(av.cliente, size="2", color="#1E293B"),
                                direction="column", gap="1",
                            ),
                            rx.flex(
                                rx.text("Atendente", size="1", color="#64748B", weight="medium"),
                                rx.text(av.responsavel, size="2", color="#1E293B"),
                                direction="column", gap="1",
                            ),
                            rx.flex(
                                rx.text("Data", size="1", color="#64748B", weight="medium"),
                                rx.text(av.data_atendimento, size="2", color="#1E293B"),
                                direction="column", gap="1",
                            ),
                            rx.flex(
                                rx.text("Duração", size="1", color="#64748B", weight="medium"),
                                rx.text(av.tempo_formatado, size="2", color="#1E293B"),
                                direction="column", gap="1",
                            ),
                            columns="2", gap="4",
                            padding="20px 24px",
                        ),
                        rx.flex(
                            rx.flex(
                                rx.text("Nota Final", size="2", weight="medium", color="#64748B"),
                                rx.flex(
                                    rx.heading(av.nota, size="8", color="#7700FF"),
                                    rx.text("/10", size="3", color="#94A3B8"),
                                    align="baseline", gap="1",
                                ),
                                direction="column", gap="1",
                            ),
                            rx.flex(
                                rx.text("Status", size="2", weight="medium", color="#64748B"),
                                rx.match(
                                    av.status,
                                    ("Excelente", rx.badge("Excelente", color_scheme="green", size="2")),
                                    ("Bom", rx.badge("Bom", color_scheme="violet", size="2")),
                                    ("Regular", rx.badge("Regular", color_scheme="orange", size="2")),
                                    ("Crítico", rx.badge("Crítico", color_scheme="red", size="2")),
                                    rx.badge("—"),
                                ),
                                direction="column", gap="2",
                            ),
                            gap="8",
                            padding="0 24px 20px",
                            border_bottom="1px solid #E2E8F0",
                        ),
                        rx.flex(
                            rx.flex(
                                rx.icon("bot", size=16, color="#6366F1"),
                                rx.text("Pontos Críticos", size="2", color="#1E293B"),
                                align="center", gap="2",
                            ),
                            rx.callout.root(
                                rx.callout.icon(rx.icon("triangle-alert", size=16)),
                                rx.callout.text(av.pontos_criticos, size="2"),
                                color="orange", variant="soft",
                            ),
                            rx.flex(
                                rx.icon("message-square", size=16, color="#22C55E"),
                                rx.text("Feedback Final", size="2", color="#1E293B"),
                                align="center", gap="2",
                            ),
                            rx.callout.root(
                                rx.callout.icon(rx.icon("circle-check", size=16)),
                                rx.callout.text(av.feedback_final, size="2"),
                                color="green", variant="soft",
                            ),
                            direction="column", gap="3",
                            padding="20px 24px",
                        ),
                        direction="column",
                        overflow_y="auto",
                        flex="1",
                    ),
                    rx.flex(
                        rx.button(rx.icon("pencil", size=14), "Revisar Nota", variant="outline", color_scheme="violet"),
                        rx.button(rx.icon("circle-x", size=14), "Desconsiderar", variant="outline", color_scheme="red"),
                        gap="3",
                        padding="16px 24px",
                        border_top="1px solid #E2E8F0",
                    ),
                    direction="column",
                    height="100%",
                    background_color="white",
                ),
                width="520px",
                height="100vh",
                top="0",
                right="0",
                position="fixed",
                background_color="white",
                box_shadow="-4px 0 24px rgba(0,0,0,0.08)",
            ),
        ),
        open=AppState.show_drawer,
        on_open_change=AppState.close_drawer,
        direction="right",
    )


def avaliacoes_content() -> rx.Component:
    return rx.flex(
        filters_bar(),
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Protocolo / Data"),
                        rx.table.column_header_cell("Cliente"),
                        rx.table.column_header_cell("Atendente"),
                        rx.table.column_header_cell("Nota"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Duração"),
                        rx.table.column_header_cell("Kanban"),
                        rx.table.column_header_cell(""),
                    ),
                    background_color="#F8FAFC",
                ),
                rx.table.body(
                    rx.foreach(AppState.avaliacoes_filtradas, table_row),
                ),
                width="100%",
                variant="ghost",
            ),
            background_color="white",
            border_radius="12px",
            border="1px solid #E2E8F0",
            overflow="hidden",
            padding="0",
        ),
        avaliacao_drawer(),
        direction="column",
        gap="0",
        width="100%",
    )


@rx.page(route="/avaliacoes", title="Avaliações — ECM", on_load=AppState.carregar_dados)
def avaliacoes() -> rx.Component:
    return page_layout(avaliacoes_content(), "Gestão de Avaliações")
