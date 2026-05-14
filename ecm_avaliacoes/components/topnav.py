import reflex as rx
from ecm_avaliacoes.state import AppState

BRAND_PURPLE = "#7700FF"
BRAND_TEAL = "#00D4C8"
BRAND_BG = "#FFFFFF"
ACTIVE_BG = BRAND_PURPLE
ACTIVE_TEXT = "#FFFFFF"
INACTIVE_TEXT = "#475569"
HOVER_BG = "#F3EEFF"

# Nav items visible to everyone (admins + atendentes)
NAV_ITEMS_ALL = [
    ("Dashboard", "layout-dashboard", "/"),
    ("Avaliações", "clipboard-list", "/avaliacoes"),
    ("Atrasos", "alarm-clock", "/atrasos"),
]

# Nav items visible to admins only
NAV_ITEMS_ADMIN = [
    ("Automação", "bot", "/automacao"),
    ("Atendentes", "users", "/atendentes"),
    ("Auditoria", "shield-check", "/auditoria"),
    ("Configurações", "settings", "/configuracoes"),
]


def nav_item(label: str, icon: str, href: str) -> rx.Component:
    is_active = AppState.current_path == href
    return rx.link(
        rx.flex(
            rx.icon(icon, size=15, color=rx.cond(is_active, ACTIVE_TEXT, INACTIVE_TEXT)),
            rx.text(
                label,
                size="2",
                weight=rx.cond(is_active, "medium", "regular"),
                color=rx.cond(is_active, ACTIVE_TEXT, INACTIVE_TEXT),
                white_space="nowrap",
            ),
            align="center",
            gap="2",
            padding="6px 12px",
            border_radius="8px",
            background=rx.cond(is_active, ACTIVE_BG, "transparent"),
            custom_attrs={"data-navhref": href},
            style={
                "_hover": {"background": rx.cond(is_active, ACTIVE_BG, HOVER_BG), "cursor": "pointer"},
                "transition": "background 0.15s ease",
            },
        ),
        href=href,
        text_decoration="none",
    )


def topnav() -> rx.Component:
    return rx.fragment(
     rx.box(
        rx.flex(
            # Logo
            rx.flex(
                rx.flex(
                    rx.box(
                        style={
                            "width": "8px",
                            "height": "8px",
                            "border_radius": "50%",
                            "background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})",
                            "margin_right": "2px",
                        }
                    ),
                    rx.text(
                        "ECM",
                        weight="bold",
                        size="4",
                        style={
                            "background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "color": "transparent",
                        },
                    ),
                    align="center",
                    gap="1",
                ),
                align="center",
                padding_right="20px",
                border_right="1px solid #E2E8F0",
                margin_right="8px",
                height="36px",
            ),
            # Nav items — always visible
            rx.flex(
                *[nav_item(label, icon, href) for label, icon, href in NAV_ITEMS_ALL],
                align="center",
                gap="1",
            ),
            # Admin-only nav items
            rx.cond(
                AppState.current_user_is_admin,
                rx.flex(
                    *[nav_item(label, icon, href) for label, icon, href in NAV_ITEMS_ADMIN],
                    align="center",
                    gap="1",
                ),
                rx.box(),
            ),
            rx.flex(flex="1"),
            # Right side: user + logout
            rx.flex(
                rx.separator(orientation="vertical", height="20px"),
                rx.flex(
                    rx.avatar(
                        fallback=AppState.current_user_nome[:2],
                        size="1",
                        style={"background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})", "color": "white"},
                    ),
                    rx.text(AppState.current_user_nome, size="2", weight="medium", color="#1E293B", white_space="nowrap"),
                    align="center",
                    gap="2",
                ),
                rx.icon_button(
                    rx.icon("log-out", size=15),
                    variant="ghost",
                    color_scheme="gray",
                    size="1",
                    on_click=AppState.fazer_logout,
                    title="Sair",
                ),
                align="center",
                gap="2",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding="0 20px",
            height="56px",
            gap="1",
        ),
        background_color=BRAND_BG,
        border_bottom="1px solid #E2E8F0",
        position="sticky",
        top="0",
        z_index="100",
        width="100%",
        box_shadow="0 1px 3px rgba(0,0,0,0.06)",
     ),
     rx.script(src="/nav_active.js"),
    )
