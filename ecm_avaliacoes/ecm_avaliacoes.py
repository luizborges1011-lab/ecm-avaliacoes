import reflex as rx
import ecm_avaliacoes.pages  # noqa: F401 — registra todas as páginas

app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "background_color": "#F1F5F9",
    },
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        ),
    ],
)
