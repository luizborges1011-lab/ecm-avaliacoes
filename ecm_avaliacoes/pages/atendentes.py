import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AtendenteItem, AvaliacaoItem

BRAND_PURPLE = "#7700FF"
BRAND_TEAL = "#00D4C8"


def nota_color(nota: float) -> rx.Var:
    return rx.cond(nota >= 8, "#22C55E", rx.cond(nota >= 6, BRAND_PURPLE, "#F59E0B"))


def nota_badge(nota: float) -> rx.Component:
    return rx.match(
        rx.cond(nota >= 8, "excelente", rx.cond(nota >= 6, "bom", rx.cond(nota >= 4, "regular", "critico"))),
        ("excelente", rx.badge(nota, color_scheme="green", variant="soft", size="1")),
        ("bom",       rx.badge(nota, color_scheme="violet", variant="soft", size="1")),
        ("regular",   rx.badge(nota, color_scheme="orange", variant="soft", size="1")),
        rx.badge(nota, color_scheme="red", variant="soft", size="1"),
    )


def avaliacao_row(av: AvaliacaoItem) -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.text(av.protocolo, size="1", color="#94A3B8", font_family="monospace"),
            rx.text(av.cliente, size="2", color="#1E293B", weight="medium"),
            direction="column", gap="0", flex="1",
        ),
        rx.flex(
            nota_badge(av.nota),
            rx.text(av.data_atendimento, size="1", color="#94A3B8"),
            align="center", gap="3",
        ),
        justify="between",
        align="center",
        padding="10px 0",
        border_bottom="1px solid #F1F5F9",
        width="100%",
    )


def stat_box(label: str, value: rx.Var, color: str = "#1E293B") -> rx.Component:
    return rx.flex(
        rx.text(value, size="6", weight="bold", color=color),
        rx.text(label, size="1", color="#94A3B8", weight="medium", text_transform="uppercase", letter_spacing="0.06em"),
        direction="column",
        align="center",
        gap="1",
        flex="1",
    )


def atendente_modal() -> rx.Component:
    stats = AppState.atendente_selecionado_stats
    return rx.dialog.root(
        rx.dialog.content(
            # Cabeçalho
            rx.box(
                rx.flex(
                    rx.flex(
                        rx.avatar(
                            fallback=AppState.selected_atendente_nome[:2],
                            size="4",
                            style={"background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})", "color": "white"},
                        ),
                        rx.flex(
                            rx.text(
                                rx.cond(AppState.filter_mes != "", AppState.filter_mes, "Todos os períodos"),
                                size="1", color="rgba(255,255,255,0.65)",
                            ),
                            rx.heading(AppState.selected_atendente_nome, size="5", color="white"),
                            direction="column", gap="0",
                        ),
                        align="center", gap="3",
                    ),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=16),
                            variant="ghost", size="2",
                            style={"color": "rgba(255,255,255,0.8)", "_hover": {"background": "rgba(255,255,255,0.15)"}},
                        ),
                    ),
                    justify="between", align="center",
                ),
                background=f"linear-gradient(135deg, {BRAND_PURPLE} 0%, #5500CC 100%)",
                padding="20px 24px",
                border_radius="12px 12px 0 0",
                margin="-24px -24px 0 -24px",
            ),
            # Stats do período
            rx.flex(
                stat_box("Atendimentos", stats["total"].to_string(), "#1E293B"),
                rx.separator(orientation="vertical", size="3"),
                stat_box("Nota Média", stats["nota_media"].to_string(), BRAND_PURPLE),
                rx.separator(orientation="vertical", size="3"),
                stat_box("Aprovados", stats["aprovados"].to_string(), "#22C55E"),
                rx.separator(orientation="vertical", size="3"),
                stat_box("Críticos", stats["criticos"].to_string(), "#EF4444"),
                justify="between",
                align="center",
                padding="20px 0",
                border_bottom="1px solid #F1F5F9",
            ),
            # Lista de atendimentos
            rx.flex(
                rx.text(
                    "Atendimentos no período",
                    size="2", weight="medium", color="#64748B",
                    padding_bottom="4px",
                ),
                rx.cond(
                    AppState.avaliacoes_do_atendente.length() > 0,
                    rx.flex(
                        rx.foreach(AppState.avaliacoes_do_atendente, avaliacao_row),
                        direction="column",
                        width="100%",
                        max_height="320px",
                        overflow_y="auto",
                    ),
                    rx.flex(
                        rx.icon("inbox", size=28, color="#CBD5E1"),
                        rx.text("Nenhum atendimento neste período", size="2", color="#94A3B8"),
                        direction="column", align="center", gap="2", padding_y="6",
                    ),
                ),
                direction="column",
                gap="2",
                padding_top="16px",
            ),
            # Fechar
            rx.flex(
                rx.dialog.close(
                    rx.button("Fechar", variant="soft", color_scheme="gray", size="2"),
                ),
                justify="end",
                padding_top="16px",
                border_top="1px solid #F1F5F9",
                margin_top="12px",
            ),
            max_width="560px",
            style={"border_radius": "12px", "padding": "24px"},
        ),
        open=AppState.show_atendente_modal,
        on_open_change=AppState.close_atendente,
    )


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
                rx.text(at.total, size="4", weight="bold", color=BRAND_PURPLE),
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
        on_click=AppState.open_atendente(at.nome),
        style={
            "_hover": {"box_shadow": f"0 4px 12px rgba(119,0,255,0.12)", "border_color": BRAND_PURPLE, "cursor": "pointer"},
            "transition": "all 0.15s ease",
        },
    )


def atendentes_content() -> rx.Component:
    return rx.flex(
        # Barra superior
        rx.flex(
            rx.input(
                rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
                placeholder="Buscar atendente...",
                value=AppState.search_atendentes,
                on_change=AppState.set_search_atendentes,
                width="260px",
                style={"background_color": "white"},
            ),
            rx.flex(
                rx.icon("calendar", size=15, color=BRAND_PURPLE),
                rx.text("Período:", size="2", color="#64748B"),
                rx.select(
                    AppState.meses_disponiveis,
                    placeholder="Selecionar mês",
                    value=AppState.filter_mes,
                    on_change=AppState.set_filter_mes,
                    width="150px",
                ),
                rx.cond(
                    AppState.filter_mes != "",
                    rx.button(
                        rx.icon("x", size=13), "Limpar",
                        variant="ghost", color_scheme="gray", size="1",
                        on_click=AppState.set_filter_mes(""),
                    ),
                    rx.box(),
                ),
                align="center", gap="2",
            ),
            justify="between", align="center", margin_bottom="5",
            flex_wrap="wrap", gap="3",
        ),
        # Label do período selecionado
        rx.cond(
            AppState.filter_mes != "",
            rx.flex(
                rx.icon("calendar-check", size=14, color=BRAND_PURPLE),
                rx.text(
                    "Exibindo dados de ",
                    rx.text.span(AppState.filter_mes, weight="bold", color=BRAND_PURPLE),
                    size="2", color="#64748B",
                ),
                align="center", gap="2",
                padding="8px 12px",
                background="#F3EEFF",
                border_radius="8px",
                border=f"1px solid #E4D0FF",
                margin_bottom="4",
            ),
            rx.box(),
        ),
        # Grid de cards
        rx.cond(
            AppState.atendentes_filtrados.length() > 0,
            rx.grid(
                rx.foreach(AppState.atendentes_filtrados, atendente_card),
                columns="3",
                gap="4",
            ),
            rx.flex(
                rx.icon("users", size=36, color="#CBD5E1"),
                rx.text("Nenhum atendimento encontrado neste período", size="3", color="#94A3B8"),
                direction="column", align="center", gap="3",
                padding_y="16",
            ),
        ),
        atendente_modal(),
        direction="column",
        width="100%",
    )


@rx.page(route="/atendentes", title="Atendentes — ECM", on_load=[AppState.verificar_auth_admin, AppState.set_mes_atual])
def atendentes() -> rx.Component:
    return page_layout(atendentes_content(), "Gestão de Atendentes")
