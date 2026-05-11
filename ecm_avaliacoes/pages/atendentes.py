import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AtendenteItem


def nota_color(nota: float) -> rx.Var:
    return rx.cond(nota >= 8, "#22C55E", rx.cond(nota >= 6, "#7700FF", "#F59E0B"))


def atendente_card(at: AtendenteItem) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.avatar(fallback=at.nome[:2], size="3", color_scheme="violet"),
                rx.flex(
                    rx.text(at.nome, size="3", weight="bold", color="#1E293B"),
                    rx.text(at.email, size="1", color="#94A3B8"),
                    direction="column", gap="0",
                ),
                align="center", gap="3", flex="1",
            ),
            rx.cond(
                at.ativo,
                rx.badge("Ativo", color_scheme="green", variant="soft"),
                rx.badge("Inativo", color_scheme="gray", variant="soft"),
            ),
            justify="between", align="start", margin_bottom="3",
        ),
        rx.separator(size="4", margin_y="3"),
        rx.flex(
            rx.flex(
                rx.text("Atendimentos", size="1", color="#64748B"),
                rx.text(at.total, size="4", weight="bold", color="#7700FF"),
                direction="column", align="center",
            ),
            rx.separator(orientation="vertical", size="3"),
            rx.flex(
                rx.text("Nota Média", size="1", color="#64748B"),
                rx.text(at.nota_media, size="4", weight="bold", color=nota_color(at.nota_media)),
                direction="column", align="center",
            ),
            justify="between", align="center",
        ),
        background_color="white",
        padding="16px",
        border_radius="12px",
        border="1px solid #E2E8F0",
        box_shadow="0 1px 3px rgba(0,0,0,0.05)",
        style={
            "_hover": {"box_shadow": "0 4px 12px rgba(119,0,255,0.1)", "border_color": "#7700FF"},
            "transition": "all 0.15s ease",
        },
    )


def atendentes_content() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.input(
                rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
                placeholder="Buscar atendente...",
                width="280px",
                style={"background_color": "white"},
            ),
            rx.flex(
                rx.button(
                    rx.icon("git-merge", size=14), "Mesclar Duplicados",
                    variant="outline", color_scheme="orange",
                ),
                rx.button(
                    rx.icon("plus", size=14), "Novo Atendente",
                    color_scheme="violet",
                ),
                gap="3",
            ),
            justify="between", align="center", margin_bottom="5",
        ),
        rx.grid(
            rx.foreach(AppState.atendentes, atendente_card),
            columns="3",
            gap="4",
        ),
        direction="column",
        width="100%",
    )


@rx.page(route="/atendentes", title="Atendentes — ECM")
def atendentes() -> rx.Component:
    return page_layout(atendentes_content(), "Gestão de Atendentes")
