import reflex as rx
from ecm_avaliacoes.components import page_layout


def config_section(title: str, description: str, content: rx.Component) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.heading(title, size="3", color="#1E293B"),
                rx.text(description, size="2", color="#64748B"),
                direction="column", gap="1",
                width="280px", flex_shrink="0",
            ),
            rx.separator(orientation="vertical", size="4"),
            rx.flex(content, flex="1", direction="column", gap="3"),
            gap="6",
            align="start",
        ),
        background_color="white",
        padding="24px",
        border_radius="12px",
        border="1px solid #E2E8F0",
    )


def configuracoes_content() -> rx.Component:
    return rx.flex(
        config_section(
            "Limites de Nota",
            "Define os limiares para classificação de atendimentos por qualidade.",
            rx.flex(
                rx.flex(
                    rx.text("Nota mínima — Excelente", size="2", weight="medium", color="#374151"),
                    rx.flex(rx.input(placeholder="8.0", default_value="8.0", width="100px"), rx.text("de 0 a 10", size="1", color="#94A3B8"), align="center", gap="2"),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Nota mínima — Bom", size="2", weight="medium", color="#374151"),
                    rx.flex(rx.input(placeholder="6.0", default_value="6.0", width="100px"), rx.text("de 0 a 10", size="1", color="#94A3B8"), align="center", gap="2"),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Nota mínima — Regular", size="2", weight="medium", color="#374151"),
                    rx.flex(rx.input(placeholder="4.0", default_value="4.0", width="100px"), rx.text("de 0 a 10", size="1", color="#94A3B8"), align="center", gap="2"),
                    justify="between", align="center",
                ),
                direction="column", gap="4",
            ),
        ),
        config_section(
            "Prazos de Análise",
            "Tempo máximo para cada etapa do fluxo de trabalho.",
            rx.flex(
                rx.flex(
                    rx.text("Prazo para Análise Humana", size="2", weight="medium", color="#374151"),
                    rx.flex(rx.input(placeholder="48", default_value="48", width="80px"), rx.text("horas", size="2", color="#94A3B8"), align="center", gap="2"),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Prazo para envio de Feedback", size="2", weight="medium", color="#374151"),
                    rx.flex(rx.input(placeholder="72", default_value="72", width="80px"), rx.text("horas", size="2", color="#94A3B8"), align="center", gap="2"),
                    justify="between", align="center",
                ),
                direction="column", gap="4",
            ),
        ),
        config_section(
            "Integração OpenAI",
            "Configurações do modelo de IA para análise de atendimentos.",
            rx.flex(
                rx.flex(
                    rx.text("Modelo de IA", size="2", weight="medium", color="#374151"),
                    rx.select(["gpt-4.1-mini", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], default_value="gpt-4.1-mini", width="200px"),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Chave API OpenAI", size="2", weight="medium", color="#374151"),
                    rx.input(placeholder="sk-...", type="password", width="280px"),
                    justify="between", align="center",
                ),
                direction="column", gap="4",
            ),
        ),
        config_section(
            "Integração Digisac",
            "Credenciais de acesso à API do Digisac.",
            rx.flex(
                rx.flex(
                    rx.text("URL da API", size="2", weight="medium", color="#374151"),
                    rx.input(default_value="https://contabilmadruga.digisac.me/api/v1", width="340px"),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Bearer Token", size="2", weight="medium", color="#374151"),
                    rx.input(placeholder="Token de autenticação", type="password", width="280px"),
                    justify="between", align="center",
                ),
                direction="column", gap="4",
            ),
        ),
        rx.flex(
            rx.button(rx.icon("save", size=14), "Salvar Configurações", color_scheme="violet", size="3"),
            justify="end",
        ),
        direction="column",
        gap="5",
        width="100%",
    )


@rx.page(route="/configuracoes", title="Configurações — ECM")
def configuracoes() -> rx.Component:
    return page_layout(configuracoes_content(), "Configurações")
