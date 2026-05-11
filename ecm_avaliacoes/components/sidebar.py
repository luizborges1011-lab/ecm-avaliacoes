import reflex as rx
from ecm_avaliacoes.state import AppState

NAV_ITEMS = [
    ("Dashboard", "layout-dashboard", "/"),
    ("Avaliações", "clipboard-list", "/avaliacoes"),
    ("Kanban", "kanban", "/kanban"),
    ("Automação", "bot", "/automacao"),
    ("Atendentes", "users", "/atendentes"),
    ("Auditoria", "shield-check", "/auditoria"),
    ("Configurações", "settings", "/configuracoes"),
]


def nav_item(label: str, icon: str, href: str) -> rx.Component:
    is_active = AppState.current_path == href
    return rx.link(
        rx.flex(
            rx.icon(
                icon,
                size=18,
                color=rx.cond(is_active, "white", "rgba(255,255,255,0.65)"),
            ),
            rx.text(
                label,
                size="2",
                weight=rx.cond(is_active, "medium", "regular"),
                color=rx.cond(is_active, "white", "rgba(255,255,255,0.65)"),
            ),
            align="center",
            gap="3",
            padding="10px 14px",
            border_radius="8px",
            background=rx.cond(is_active, "rgba(255,255,255,0.18)", "transparent"),
            width="100%",
            style={
                "_hover": {"background": "rgba(255,255,255,0.10)"},
                "transition": "background 0.15s ease",
            },
        ),
        href=href,
        text_decoration="none",
        width="100%",
        display="block",
    )


def sidebar() -> rx.Component:
    return rx.box(
        # Logo
        rx.flex(
            rx.flex(
                rx.box(
                    rx.text("ECM", weight="bold", size="5", color="white"),
                    rx.text(
                        "Avaliações",
                        size="1",
                        color="rgba(255,255,255,0.6)",
                        letter_spacing="0.08em",
                    ),
                    text_align="center",
                ),
                align="center",
                justify="center",
                width="100%",
                padding_y="6",
            ),
            width="100%",
            border_bottom="1px solid rgba(255,255,255,0.12)",
        ),
        # Navigation
        rx.flex(
            *[nav_item(label, icon, href) for label, icon, href in NAV_ITEMS],
            direction="column",
            gap="1",
            padding="12px 10px",
            width="100%",
        ),
        # Bottom user info
        rx.box(
            rx.flex(
                rx.avatar(fallback="LB", size="2", color_scheme="violet"),
                rx.flex(
                    rx.text("Luiz Borges", color="white", size="2", weight="medium"),
                    rx.text("Administrador", color="rgba(255,255,255,0.55)", size="1"),
                    direction="column",
                    gap="0",
                ),
                align="center",
                gap="3",
            ),
            padding="14px 16px",
            border_top="1px solid rgba(255,255,255,0.12)",
            position="absolute",
            bottom="0",
            width="100%",
        ),
        position="fixed",
        left="0",
        top="0",
        width="220px",
        height="100vh",
        background_color="#7700FF",
        z_index="100",
        overflow="hidden",
    )
