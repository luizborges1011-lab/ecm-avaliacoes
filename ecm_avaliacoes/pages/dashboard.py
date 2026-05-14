import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import RankingItem, AvaliacaoItem


def kpi_card(title: str, value: rx.Var, icon: str, bg_color: str, subtitle: str = "") -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.text(title, size="1", color="#64748B", weight="medium", text_transform="uppercase", letter_spacing="0.05em"),
                rx.heading(value, size="7", color="#0F172A"),
                rx.text(subtitle, size="1", color="#94A3B8") if subtitle else rx.box(),
                direction="column",
                gap="1",
                flex="1",
            ),
            rx.flex(
                rx.icon(icon, size=22, color="white"),
                width="48px",
                height="48px",
                min_width="48px",
                background_color=bg_color,
                border_radius="12px",
                align="center",
                justify="center",
            ),
            justify="between",
            align="start",
            width="100%",
        ),
        background_color="white",
        padding="20px",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        border_radius="12px",
        border="1px solid #F1F5F9",
        style={"_hover": {"box_shadow": "0 4px 12px rgba(119,0,255,0.1)"}, "transition": "box-shadow 0.2s ease"},
    )


def ranking_item(item: RankingItem) -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.text(
                item.posicao,
                size="2",
                weight="bold",
                color=rx.cond(item.posicao == 1, "#F59E0B", rx.cond(item.posicao <= 3, "#94A3B8", "#CBD5E1")),
                width="20px",
                text_align="center",
            ),
            rx.avatar(fallback=item.nome[:2], size="2", color_scheme="violet"),
            rx.flex(
                rx.text(item.nome, size="2", weight="medium", color="#1E293B"),
                rx.text(item.total, " atend.", size="1", color="#94A3B8"),
                direction="column",
                gap="0",
            ),
            align="center",
            gap="3",
            flex="1",
        ),
        rx.flex(
            rx.text(item.nota, size="3", color="#7700FF"),
            rx.text("/10", size="1", color="#94A3B8"),
            align="baseline",
            gap="1",
        ),
        justify="between",
        align="center",
        padding="10px 0",
        border_bottom="1px solid #F1F5F9",
        width="100%",
    )


def alert_item(av: AvaliacaoItem) -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.badge(av.status, color_scheme="red", variant="soft"),
            rx.flex(
                rx.text(av.cliente, size="2", weight="medium", color="#1E293B"),
                rx.text(av.responsavel, size="1", color="#64748B"),
                direction="column",
                gap="0",
            ),
            align="center",
            gap="3",
            flex="1",
        ),
        rx.flex(
            rx.text(av.nota, size="3", color="#EF4444"),
            rx.icon("arrow-right", size=14, color="#EF4444"),
            align="center",
            gap="1",
        ),
        justify="between",
        align="center",
        padding="10px 12px",
        border_bottom="1px solid #FEF2F2",
        border_radius="8px",
        width="100%",
        cursor="pointer",
        on_click=AppState.navegar_para_avaliacao(av.id),
        style={
            "_hover": {
                "background_color": "#FEF2F2",
                "box_shadow": "0 2px 8px rgba(239,68,68,0.12)",
            },
            "transition": "background-color 0.15s ease, box-shadow 0.15s ease",
        },
    )


def chart_section() -> rx.Component:
    return rx.grid(
        rx.card(
            rx.flex(
                rx.heading("Evolução da Nota Média", size="3", color="#1E293B"),
                rx.text("Últimos 7 meses", size="1", color="#94A3B8"),
                direction="column",
                gap="1",
                margin_bottom="4",
            ),
            rx.recharts.responsive_container(
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#F1F5F9"),
                    rx.recharts.x_axis(data_key="mes", tick={"fontSize": 12, "fill": "#94A3B8"}),
                    rx.recharts.y_axis(domain=[6, 10], tick={"fontSize": 12, "fill": "#94A3B8"}),
                    rx.recharts.graphing_tooltip(
                        content_style={"background": "white", "border": "1px solid #E2E8F0", "borderRadius": "8px"}
                    ),
                    rx.recharts.line(data_key="nota_media", stroke="#7700FF", stroke_width=2.5, dot={"fill": "#7700FF", "r": 4}, name="Nota Média"),
                    data=AppState.monthly_data,
                ),
                width="100%",
                height=260,
            ),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #F1F5F9",
            box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        ),
        rx.card(
            rx.flex(
                rx.heading("Volume de Atendimentos", size="3", color="#1E293B"),
                rx.text("Atendimentos avaliados por mês", size="1", color="#94A3B8"),
                direction="column",
                gap="1",
                margin_bottom="4",
            ),
            rx.recharts.responsive_container(
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#F1F5F9"),
                    rx.recharts.x_axis(data_key="mes", tick={"fontSize": 12, "fill": "#94A3B8"}),
                    rx.recharts.y_axis(tick={"fontSize": 12, "fill": "#94A3B8"}),
                    rx.recharts.graphing_tooltip(
                        content_style={"background": "white", "border": "1px solid #E2E8F0", "borderRadius": "8px"}
                    ),
                    rx.recharts.bar(data_key="total", fill="#7700FF", radius=[4, 4, 0, 0], name="Total"),
                    data=AppState.monthly_data,
                ),
                width="100%",
                height=260,
            ),
            background_color="white",
            padding="20px",
            border_radius="12px",
            border="1px solid #F1F5F9",
            box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        ),
        columns="2",
        gap="5",
    )


def volume_item(item: RankingItem) -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.text(
                item.posicao,
                size="2",
                weight="bold",
                color=rx.cond(item.posicao == 1, "#F59E0B", rx.cond(item.posicao <= 3, "#94A3B8", "#CBD5E1")),
                width="20px",
                text_align="center",
            ),
            rx.avatar(fallback=item.nome[:2], size="2", color_scheme="teal"),
            rx.flex(
                rx.text(item.nome, size="2", weight="medium", color="#1E293B"),
                rx.text("média ", item.nota, "/10", size="1", color="#94A3B8"),
                direction="column",
                gap="0",
            ),
            align="center",
            gap="3",
            flex="1",
        ),
        rx.flex(
            rx.text(item.total, size="3", color="#0D9488"),
            rx.text(" chams.", size="1", color="#94A3B8"),
            align="baseline",
            gap="1",
        ),
        justify="between",
        align="center",
        padding="10px 0",
        border_bottom="1px solid #F1F5F9",
        width="100%",
    )


def ranking_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("trophy", size=18, color="#F59E0B"),
                rx.heading("Top 7 — Nota", size="3", color="#1E293B"),
                align="center",
                gap="2",
            ),
            rx.text("Nota média do período", size="1", color="#94A3B8"),
            justify="between",
            align="center",
            margin_bottom="4",
        ),
        rx.flex(
            rx.foreach(AppState.ranking_data, ranking_item),
            direction="column",
            width="100%",
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #F1F5F9",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
    )


def volume_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("bar-chart-2", size=18, color="#0D9488"),
                rx.heading("Top 7 — Volume", size="3", color="#1E293B"),
                align="center",
                gap="2",
            ),
            rx.text("Mais atendimentos no período", size="1", color="#94A3B8"),
            justify="between",
            align="center",
            margin_bottom="4",
        ),
        rx.flex(
            rx.foreach(AppState.ranking_volume_data, volume_item),
            direction="column",
            width="100%",
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #F1F5F9",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
    )


def alerts_section() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("triangle-alert", size=18, color="#EF4444"),
                rx.heading("Atenção Necessária", size="3", color="#1E293B"),
                align="center",
                gap="2",
            ),
            rx.text("Avaliações abaixo de 6.0", size="1", color="#94A3B8"),
            justify="between",
            align="center",
            margin_bottom="4",
        ),
        rx.cond(
            AppState.avaliacoes_criticas.length() > 0,
            rx.flex(
                rx.foreach(AppState.avaliacoes_criticas, alert_item),
                direction="column",
                width="100%",
            ),
            rx.flex(
                rx.icon("circle-check", size=32, color="#22C55E"),
                rx.text("Nenhuma avaliação crítica", size="2", color="#64748B"),
                direction="column",
                align="center",
                gap="2",
                padding="24px",
            ),
        ),
        background_color="white",
        padding="20px",
        border_radius="12px",
        border="1px solid #F1F5F9",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
    )


def mes_filter_bar() -> rx.Component:
    return rx.flex(
        rx.icon("calendar", size=16, color="#7700FF"),
        rx.text("Período:", size="2", color="#64748B"),
        rx.select(
            AppState.meses_disponiveis,
            placeholder="Todos os meses",
            value=AppState.filter_mes,
            on_change=AppState.set_filter_mes,
            width="160px",
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
        align="center",
        gap="2",
    )


def dashboard_content() -> rx.Component:
    return rx.flex(
        mes_filter_bar(),
        rx.grid(
            kpi_card("Nota Média", AppState.nota_media, "star", "#7700FF", "de 0 a 10"),
            kpi_card("Total de Avaliações", AppState.total_avaliacoes.to_string(), "clipboard-list", "#7700FF", "no período"),
            kpi_card("Tempo Médio", AppState.tempo_medio, "clock", "#6366F1", "por atendimento"),
            kpi_card("Taxa de Aprovação", AppState.taxa_aprovacao, "circle-check", "#22C55E", "nota ≥ 7.0"),
            columns="4",
            gap="5",
        ),
        chart_section(),
        rx.grid(
            ranking_section(),
            volume_section(),
            alerts_section(),
            columns="3",
            gap="5",
        ),
        direction="column",
        gap="5",
        width="100%",
    )


@rx.page(route="/", title="Dashboard — ECM Avaliações", on_load=AppState.verificar_auth)
def dashboard() -> rx.Component:
    return page_layout(dashboard_content(), "Dashboard")
