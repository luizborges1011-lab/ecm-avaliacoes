import reflex as rx
from ecm_avaliacoes.state import AppState

BRAND_PURPLE = "#7700FF"
BRAND_TEAL = "#00D4C8"


@rx.page(route="/login", title="Login — ECM Avaliações")
def login() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.card(
                rx.flex(
                    # Logo
                    rx.flex(
                        rx.flex(
                            rx.box(
                                style={
                                    "width": "10px",
                                    "height": "10px",
                                    "border_radius": "50%",
                                    "background": f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})",
                                    "margin_right": "3px",
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
                            gap="1",
                        ),
                        justify="center",
                        margin_bottom="2",
                    ),
                    rx.text(
                        "Avaliações",
                        size="2",
                        color="#94A3B8",
                        text_align="center",
                        margin_bottom="6",
                    ),
                    # Form
                    rx.flex(
                        rx.text("E-mail", size="2", weight="medium", color="#374151"),
                        rx.input(
                            placeholder="seu@email.com.br",
                            type="email",
                            value=AppState.login_email,
                            on_change=AppState.set_login_email,
                            style={"width": "100%"},
                        ),
                        direction="column",
                        gap="1",
                        width="100%",
                    ),
                    rx.flex(
                        rx.text("Senha", size="2", weight="medium", color="#374151"),
                        rx.input(
                            placeholder="••••••••",
                            type="password",
                            value=AppState.login_senha,
                            on_change=AppState.set_login_senha,
                            on_key_down=rx.cond(
                                rx.Var.create("event.key") == "Enter",
                                AppState.fazer_login,
                                rx.noop(),
                            ),
                            style={"width": "100%"},
                        ),
                        direction="column",
                        gap="1",
                        width="100%",
                        margin_top="3",
                    ),
                    rx.cond(
                        AppState.login_error != "",
                        rx.callout(
                            AppState.login_error,
                            icon="triangle-alert",
                            color_scheme="red",
                            size="1",
                            margin_top="3",
                        ),
                        rx.box(),
                    ),
                    rx.button(
                        rx.cond(
                            AppState.login_loading,
                            rx.flex(
                                rx.spinner(size="1"),
                                rx.text("Entrando..."),
                                align="center",
                                gap="2",
                            ),
                            rx.text("Entrar"),
                        ),
                        color_scheme="violet",
                        width="100%",
                        size="3",
                        margin_top="5",
                        on_click=AppState.fazer_login,
                        disabled=AppState.login_loading,
                    ),
                    direction="column",
                    align="stretch",
                    width="100%",
                ),
                background_color="white",
                padding="36px",
                border_radius="16px",
                border="1px solid #E2E8F0",
                box_shadow="0 4px 24px rgba(0,0,0,0.08)",
                width="360px",
            ),
            justify="center",
            align="center",
            min_height="100vh",
        ),
        background_color="#F1F5F9",
        width="100%",
        min_height="100vh",
    )
