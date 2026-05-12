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


def page_layout(content: rx.Component, title: str = "") -> rx.Component:
    return rx.box(
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
