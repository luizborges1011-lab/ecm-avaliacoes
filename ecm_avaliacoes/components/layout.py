import reflex as rx
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.components.topnav import topnav

BRAND_PURPLE = "#7700FF"
BRAND_TEAL = "#00D4C8"


def top_bar(title: str = "") -> rx.Component:
    """Kept for backward compatibility — renders the page title bar below the topnav."""
    return rx.flex(
        rx.heading(title, size="4", color="#1E293B", weight="bold"),
        justify="start",
        align="center",
        padding="0px 24px",
        height="48px",
        background_color="white",
        border_bottom="1px solid #E2E8F0",
    )


def _auth_loading_overlay() -> rx.Component:
    return rx.cond(
        AppState.is_auth_checking,
        rx.box(
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.box(
                            style={
                                "width": "10px",
                                "height": "10px",
                                "border_radius": "50%",
                                "background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})",
                            }
                        ),
                        rx.text(
                            "ECM",
                            weight="bold",
                            size="5",
                            style={
                                "background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})",
                                "background_clip": "text",
                                "-webkit-background-clip": "text",
                                "color": "transparent",
                            },
                        ),
                        align="center",
                        gap="2",
                        margin_bottom="24px",
                    ),
                    rx.spinner(size="3", color_scheme="violet"),
                    direction="column",
                    align="center",
                    gap="0",
                ),
                align="center",
                justify="center",
                width="100%",
                height="100vh",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            background_color="white",
            z_index="9999",
        ),
        rx.box(),
    )


def page_layout(content: rx.Component, title: str = "") -> rx.Component:
    return rx.box(
        _auth_loading_overlay(),
        rx.toast.provider(),
        rx.cond(
            ~AppState.tv_mode,
            topnav(),
            rx.box(),
        ),
        rx.cond(
            ~AppState.tv_mode,
            top_bar(title),
            rx.box(),
        ),
        rx.box(
            content,
            padding="24px",
            min_height="calc(100vh - 104px)",
            background_color="#F8F5FF",
        ),
        width="100%",
        position="relative",
    )
