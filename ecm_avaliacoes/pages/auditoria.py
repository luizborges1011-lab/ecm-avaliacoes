import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AuditLogItem


def audit_row(log: AuditLogItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.avatar(
                    fallback=log.usuario[:2],
                    size="1",
                    color_scheme=rx.cond(log.usuario == "Sistema", "gray", "blue"),
                ),
                rx.text(log.usuario, size="2", color="#374151"),
                align="center", gap="2",
            )
        ),
        rx.table.cell(
            rx.match(
                log.acao,
                ("Nota revisada", rx.badge("Nota revisada", color_scheme="violet", variant="soft", size="1")),
                ("Status Kanban alterado", rx.badge("Kanban", color_scheme="purple", variant="soft", size="1")),
                ("Avaliação desconsiderada", rx.badge("Desconsiderada", color_scheme="orange", variant="soft", size="1")),
                ("Avaliação processada", rx.badge("Processamento", color_scheme="green", variant="soft", size="1")),
                rx.badge(log.acao, size="1"),
            )
        ),
        rx.table.cell(rx.text(log.entidade_id, size="1", color="#94A3B8", font_family="monospace")),
        rx.table.cell(rx.text(log.detalhes, size="2", color="#64748B")),
        rx.table.cell(rx.text(log.criado_em, size="1", color="#94A3B8")),
        style={"_hover": {"background_color": "#F8FAFC"}},
    )


def auditoria_content() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.input(
                rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
                placeholder="Buscar nos logs...",
                width="280px",
                style={"background_color": "white"},
            ),
            rx.select(
                ["Todos", "Nota revisada", "Status Kanban alterado", "Avaliação desconsiderada", "Avaliação processada"],
                placeholder="Tipo de ação",
                width="200px",
            ),
            rx.flex(flex="1"),
            rx.button(rx.icon("download", size=14), "Exportar", variant="outline", color_scheme="violet"),
            align="center", gap="3", margin_bottom="5",
        ),
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Usuário"),
                        rx.table.column_header_cell("Ação"),
                        rx.table.column_header_cell("Protocolo"),
                        rx.table.column_header_cell("Detalhes"),
                        rx.table.column_header_cell("Data / Hora"),
                    ),
                    background_color="#F8FAFC",
                ),
                rx.table.body(rx.foreach(AppState.audit_logs, audit_row)),
                width="100%", variant="ghost",
            ),
            background_color="white",
            border_radius="12px",
            border="1px solid #E2E8F0",
            overflow="hidden",
            padding="0",
        ),
        direction="column",
        width="100%",
    )


@rx.page(route="/auditoria", title="Auditoria — ECM")
def auditoria() -> rx.Component:
    return page_layout(auditoria_content(), "Log de Auditoria")
