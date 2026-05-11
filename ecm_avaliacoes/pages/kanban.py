import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AvaliacaoItem


def nota_color(nota: float) -> rx.Var:
    return rx.cond(nota >= 8, "#22C55E", rx.cond(nota >= 6, "#7700FF", rx.cond(nota >= 4, "#F59E0B", "#EF4444")))


def kanban_card(av: AvaliacaoItem) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.text(av.nota, size="2", weight="bold", color=nota_color(av.nota)),
                rx.text("/10", size="1", color="#94A3B8"),
                align="baseline", gap="1",
            ),
            rx.match(
                av.status,
                ("Excelente", rx.badge("Excelente", color_scheme="green", size="1", variant="soft")),
                ("Bom", rx.badge("Bom", color_scheme="violet", size="1", variant="soft")),
                ("Regular", rx.badge("Regular", color_scheme="orange", size="1", variant="soft")),
                ("Crítico", rx.badge("Crítico", color_scheme="red", size="1", variant="soft")),
                rx.badge(av.status, size="1"),
            ),
            justify="between", align="center", margin_bottom="2",
        ),
        rx.text(av.cliente, size="2", weight="bold", color="#1E293B", margin_bottom="1"),
        rx.flex(
            rx.avatar(fallback=av.responsavel[:2], size="1", color_scheme="violet"),
            rx.text(av.responsavel, size="1", color="#64748B"),
            align="center", gap="2", margin_bottom="2",
        ),
        rx.flex(
            rx.icon("clock", size=12, color="#94A3B8"),
            rx.text(av.tempo_formatado, size="1", color="#94A3B8"),
            rx.flex(flex="1"),
            rx.text(av.data_atendimento, size="1", color="#CBD5E1"),
            align="center", gap="1",
        ),
        background_color="white",
        border_radius="8px",
        padding="12px",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        border="1px solid #E2E8F0",
        width="100%",
        cursor="pointer",
        on_click=AppState.open_avaliacao(av.id),
        style={
            "_hover": {"box_shadow": "0 4px 12px rgba(119,0,255,0.1)", "border_color": "#7700FF"},
            "transition": "all 0.15s ease",
        },
    )


def kanban_column(
    title: str,
    state_var,
    scheme: str,
    icon: str,
) -> rx.Component:
    count = state_var.length()
    return rx.flex(
        rx.flex(
            rx.flex(
                rx.icon(icon, size=15,
                        color=rx.match(
                            scheme,
                            ("gray", "#94A3B8"),
                            ("orange", "#F59E0B"),
                            ("purple", "#8B5CF6"),
                            ("yellow", "#EAB308"),
                            ("green", "#22C55E"),
                            "#94A3B8",
                        )),
                rx.text(title, size="2", weight="bold", color="#374151"),
                align="center", gap="2",
            ),
            rx.badge(count, color_scheme=scheme, variant="soft", size="1"),
            justify="between", align="center",
            padding="12px 14px",
            border_bottom="1px solid #E2E8F0",
        ),
        rx.flex(
            rx.foreach(state_var, kanban_card),
            direction="column",
            gap="3",
            padding="12px",
            overflow_y="auto",
            flex="1",
        ),
        direction="column",
        background_color="#F8FAFC",
        border_radius="10px",
        border="1px solid #E2E8F0",
        min_width="260px",
        max_width="280px",
        flex="1",
        height="calc(100vh - 160px)",
    )


def kanban_content() -> rx.Component:
    return rx.flex(
        kanban_column("Pendente", AppState.avaliacoes_pendentes, "gray", "clock"),
        kanban_column("Análise Humana", AppState.avaliacoes_analise, "orange", "user-check"),
        kanban_column("Feedback", AppState.avaliacoes_feedback, "purple", "message-circle"),
        kanban_column("Com Ressalvas", AppState.avaliacoes_com_ressalvas, "yellow", "triangle-alert"),
        kanban_column("Concluído", AppState.avaliacoes_sem_ressalvas, "green", "circle-check"),
        gap="4",
        overflow_x="auto",
        width="100%",
        padding_bottom="8px",
    )


@rx.page(route="/kanban", title="Kanban — ECM", on_load=AppState.carregar_dados)
def kanban() -> rx.Component:
    return page_layout(kanban_content(), "Fluxo de Trabalho")
