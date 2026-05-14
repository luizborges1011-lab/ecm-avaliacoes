import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AtrasadoAgrupadoItem, DeptAtrasoItem

ORANGE = "#F97316"
ORANGE_SOFT = "#FFF7ED"
ORANGE_BORDER = "#FDBA74"
AMBER = "#F59E0B"


def dept_card(item: DeptAtrasoItem) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.icon("building-2", size=14, color=ORANGE),
                rx.text(item.setor, size="2", weight="medium", color="#1E293B", no_wrap=True),
                align="center", gap="2",
            ),
            rx.flex(
                rx.flex(
                    rx.text(item.clientes, size="5", weight="bold", color=ORANGE),
                    rx.text("clientes", size="1", color="#94A3B8"),
                    direction="column", align="center", gap="0",
                ),
                rx.separator(orientation="vertical", size="2"),
                rx.flex(
                    rx.text(item.ocorrencias, size="5", weight="bold", color="#64748B"),
                    rx.text("alertas", size="1", color="#94A3B8"),
                    direction="column", align="center", gap="0",
                ),
                align="center", gap="3",
            ),
            direction="column", gap="3",
        ),
        background_color="white",
        padding="14px 18px",
        border_radius="10px",
        border="1px solid " + ORANGE_BORDER,
        min_width="160px",
        style={
            "_hover": {"border_color": ORANGE, "box_shadow": "0 2px 8px rgba(249,115,22,0.12)"},
            "transition": "all 0.15s ease",
            "cursor": "pointer",
        },
        on_click=AppState.set_filter_setor_atrasos(item.setor),
    )


def dept_cards_section() -> rx.Component:
    return rx.cond(
        AppState.atrasos_por_departamento.length() > 0,
        rx.flex(
            rx.flex(
                rx.icon("building-2", size=14, color="#64748B"),
                rx.text(
                    "Clientes afetados por departamento",
                    size="2", color="#64748B", weight="medium",
                ),
                rx.text("· clique para filtrar", size="1", color="#94A3B8"),
                align="center", gap="2",
            ),
            rx.flex(
                rx.foreach(AppState.atrasos_por_departamento, dept_card),
                gap="3",
                flex_wrap="wrap",
            ),
            direction="column",
            gap="3",
            padding="16px",
            background=ORANGE_SOFT,
            border="1px solid " + ORANGE_BORDER,
            border_radius="10px",
        ),
        rx.box(),
    )


def kpi_atraso(title: str, value, icon: str, color: str, subtitle: str = "") -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.text(
                    title, size="1", color="#64748B", weight="medium",
                    text_transform="uppercase", letter_spacing="0.05em",
                ),
                rx.heading(value, size="7", color="#0F172A"),
                rx.text(subtitle, size="1", color="#94A3B8") if subtitle else rx.box(),
                direction="column",
                gap="1",
                flex="1",
            ),
            rx.flex(
                rx.icon(icon, size=22, color="white"),
                width="48px", height="48px", min_width="48px",
                background_color=color,
                border_radius="12px",
                align="center", justify="center",
            ),
            justify="between", align="start", width="100%",
        ),
        background_color="white",
        padding="20px",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
        border_radius="12px",
        border="1px solid #F1F5F9",
        style={
            "_hover": {"box_shadow": "0 4px 12px rgba(249,115,22,0.15)"},
            "transition": "box-shadow 0.2s ease",
        },
    )


def ocorrencias_badge(item: AtrasadoAgrupadoItem) -> rx.Component:
    return rx.cond(
        item.total_esperas >= 5,
        rx.badge(
            rx.flex(rx.icon("flame", size=11), item.total_esperas, align="center", gap="1"),
            color_scheme="red", variant="solid", size="2",
        ),
        rx.cond(
            item.total_esperas >= 3,
            rx.badge(
                rx.flex(rx.icon("triangle-alert", size=11), item.total_esperas, align="center", gap="1"),
                color_scheme="orange", variant="solid", size="2",
            ),
            rx.badge(item.total_esperas, color_scheme="amber", variant="soft", size="2"),
        ),
    )


def atraso_row(item: AtrasadoAgrupadoItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.flex(
                    rx.text(item.cliente[:2], size="1", weight="bold", color="white"),
                    width="30px", height="30px",
                    background="linear-gradient(135deg, #F97316, #FBBF24)",
                    border_radius="50%",
                    align="center", justify="center",
                    flex_shrink="0",
                ),
                rx.text(item.cliente, size="2", weight="medium", color="#1E293B"),
                align="center", gap="2",
            ),
            min_width="160px",
        ),
        rx.table.cell(
            ocorrencias_badge(item),
            text_align="center",
        ),
        rx.table.cell(
            rx.badge(item.setores, color_scheme="violet", variant="soft", size="1"),
        ),
        rx.table.cell(
            rx.text(
                item.protocolos, size="1", color="#64748B",
                font_family="monospace",
                max_width="240px",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                display="block",
            ),
        ),
        rx.table.cell(
            rx.flex(
                rx.icon("calendar", size=12, color="#94A3B8"),
                rx.text(item.ultima_data, size="1", color="#94A3B8"),
                align="center", gap="1",
            ),
        ),
        style={"_hover": {"background_color": "#FFF7ED"}, "cursor": "default"},
    )


def empty_state() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.flex(
                rx.icon("circle-check", size=40, color="#22C55E"),
                width="80px", height="80px",
                background="#F0FDF4",
                border_radius="50%",
                align="center", justify="center",
            ),
            rx.heading("Nenhum atraso registrado", size="4", color="#1E293B"),
            rx.text(
                "Não há chamados com espera registrada no período selecionado.",
                size="2", color="#64748B", text_align="center", max_width="380px",
            ),
            direction="column", align="center", gap="3",
        ),
        justify="center", align="center",
        padding="64px 0",
        width="100%",
    )


def _filter_label(text: str) -> rx.Component:
    return rx.text(text, size="1", color="#64748B", weight="medium")


def filters_bar() -> rx.Component:
    return rx.flex(
        # Busca
        rx.flex(
            _filter_label("Buscar"),
            rx.input(
                rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
                placeholder="Buscar por cliente...",
                value=AppState.atrasos_search,
                on_change=AppState.set_atrasos_search,
                width="260px",
                style={"background_color": "white"},
            ),
            direction="column", gap="1",
        ),
        # Período
        rx.flex(
            _filter_label("Período"),
            rx.select(
                AppState.meses_atrasos_com_todos,
                value=AppState.filter_mes_atrasos_display,
                on_change=AppState.set_filter_mes_atrasos,
                width="160px",
            ),
            direction="column", gap="1",
        ),
        # Inputs de data personalizada
        rx.cond(
            AppState.usar_periodo_personalizado,
            rx.flex(
                _filter_label("De"),
                rx.input(
                    type="date",
                    value=AppState.filter_data_inicio_atrasos,
                    on_change=AppState.set_filter_data_inicio_atrasos,
                    width="150px",
                    style={"background_color": "white"},
                ),
                direction="column", gap="1",
            ),
            rx.box(),
        ),
        rx.cond(
            AppState.usar_periodo_personalizado,
            rx.flex(
                _filter_label("Até"),
                rx.input(
                    type="date",
                    value=AppState.filter_data_fim_atrasos,
                    on_change=AppState.set_filter_data_fim_atrasos,
                    width="150px",
                    style={"background_color": "white"},
                ),
                direction="column", gap="1",
            ),
            rx.box(),
        ),
        # Departamento
        rx.flex(
            _filter_label("Departamento"),
            rx.select(
                AppState.setores_com_todos_atrasos,
                value=AppState.filter_setor_atrasos_display,
                on_change=AppState.set_filter_setor_atrasos,
                width="180px",
            ),
            direction="column", gap="1",
        ),
        # Limpar
        rx.flex(
            rx.box(height="16px"),
            rx.button(
                rx.icon("x", size=14), "Limpar",
                variant="ghost", color_scheme="gray", size="2",
                on_click=AppState.clear_atrasos_filters,
            ),
            direction="column", gap="1",
        ),
        align="end",
        gap="3",
        padding="16px 0",
        flex_wrap="wrap",
    )


def summary_banner() -> rx.Component:
    return rx.cond(
        AppState.atrasos_total_registros > 0,
        rx.box(
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.icon("alarm-clock", size=18, color=ORANGE),
                        width="36px", height="36px",
                        background=ORANGE_SOFT,
                        border_radius="10px",
                        align="center", justify="center",
                        flex_shrink="0",
                    ),
                    rx.flex(
                        rx.flex(
                            rx.text(AppState.atrasos_total_registros, size="2", weight="bold", color="#9A3412"),
                            rx.text(" notificações de espera —", size="2", color="#9A3412"),
                            rx.text(AppState.atrasos_total_clientes, size="2", weight="bold", color="#9A3412"),
                            rx.text(" clientes afetados", size="2", color="#9A3412"),
                            align="center", gap="1", flex_wrap="wrap",
                        ),
                        rx.text(
                            "Chamados que ultrapassaram o limite de espera na fila de atendimento.",
                            size="1", color="#C2410C",
                        ),
                        direction="column", gap="1",
                    ),
                    align="center", gap="3",
                ),
                rx.cond(
                    AppState.filter_mes_atrasos != "",
                    rx.badge(
                        rx.icon("calendar", size=11), " ", AppState.filter_mes_atrasos,
                        color_scheme="orange", variant="soft", size="1",
                    ),
                    rx.box(),
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            background=ORANGE_SOFT,
            border="1px solid " + ORANGE_BORDER,
            border_radius="10px",
            padding="12px 16px",
            margin_bottom="4px",
        ),
        rx.box(),
    )


def atrasos_content() -> rx.Component:
    return rx.flex(
        # KPI Cards
        rx.grid(
            kpi_atraso(
                "Total de Notificações",
                AppState.atrasos_total_registros,
                "alarm-clock",
                ORANGE,
                "registros de espera",
            ),
            kpi_atraso(
                "Clientes Afetados",
                AppState.atrasos_total_clientes,
                "users",
                "#7700FF",
                "clientes únicos",
            ),
            kpi_atraso(
                "Protocolos Envolvidos",
                AppState.atrasos_total_protocolos,
                "hash",
                AMBER,
                "chamados distintos",
            ),
            kpi_atraso(
                "Setor Mais Afetado",
                AppState.atrasos_setor_mais_afetado,
                "building-2",
                "#00D4C8",
                "maior volume",
            ),
            columns="4",
            gap="4",
            width="100%",
        ),
        # Cards por departamento
        dept_cards_section(),
        # Filtros
        filters_bar(),
        # Banner de resumo
        summary_banner(),
        # Tabela
        rx.card(
            rx.cond(
                AppState.atrasados_agrupados.length() == 0,
                empty_state(),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(
                                rx.flex(rx.icon("user", size=13, color="#64748B"), "Cliente", align="center", gap="2")
                            ),
                            rx.table.column_header_cell(
                                rx.flex(rx.icon("repeat", size=13, color="#64748B"), "Ocorrências", align="center", gap="2"),
                                text_align="center",
                            ),
                            rx.table.column_header_cell(
                                rx.flex(rx.icon("building-2", size=13, color="#64748B"), "Setor", align="center", gap="2")
                            ),
                            rx.table.column_header_cell(
                                rx.flex(rx.icon("hash", size=13, color="#64748B"), "Protocolo(s)", align="center", gap="2")
                            ),
                            rx.table.column_header_cell(
                                rx.flex(rx.icon("calendar", size=13, color="#64748B"), "Última Ocorrência", align="center", gap="2")
                            ),
                            style={"background_color": "#FFF7ED"},
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(AppState.atrasados_agrupados, atraso_row),
                    ),
                    width="100%",
                    variant="ghost",
                ),
            ),
            background_color="white",
            border_radius="12px",
            border="1px solid #FED7AA",
            overflow="hidden",
            padding="0",
        ),
        direction="column",
        gap="4",
        width="100%",
    )


@rx.page(route="/atrasos", title="Atrasos — ECM", on_load=AppState.verificar_auth)
def atrasos() -> rx.Component:
    return page_layout(atrasos_content(), "Atendimentos em Atraso")
