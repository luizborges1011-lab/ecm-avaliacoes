import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState


def _swatch(scheme: str, hex_color: str) -> rx.Component:
    selected = AppState.config_etiqueta_revisao_cor == scheme
    return rx.box(
        rx.cond(
            selected,
            rx.icon("check", size=13, color="white"),
            rx.box(),
        ),
        background_color=hex_color,
        width="28px",
        height="28px",
        min_width="28px",
        border_radius="6px",
        cursor="pointer",
        display="flex",
        align_items="center",
        justify_content="center",
        on_click=AppState.set_config_etiqueta_revisao_cor(scheme),
        style={
            "outline": rx.cond(selected, f"3px solid {hex_color}", "3px solid transparent"),
            "outline_offset": "2px",
            "transition": "outline 0.1s ease, transform 0.1s ease",
            "_hover": {"transform": "scale(1.18)"},
        },
    )


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


def user_badge(is_admin: bool) -> rx.Component:
    return rx.cond(
        is_admin,
        rx.badge("Admin", color_scheme="violet", variant="solid", size="1"),
        rx.badge("Atendente", color_scheme="gray", variant="soft", size="1"),
    )


def user_status_badge(ativo: bool) -> rx.Component:
    return rx.cond(
        ativo,
        rx.badge("Ativo", color_scheme="green", variant="soft", size="1"),
        rx.badge("Inativo", color_scheme="red", variant="soft", size="1"),
    )


def user_row(user) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.avatar(fallback=user.nome[:2], size="1", color_scheme="violet"),
                rx.flex(
                    rx.text(user.nome, size="2", weight="medium", color="#1E293B"),
                    rx.text(user.email, size="1", color="#94A3B8"),
                    direction="column", gap="0",
                ),
                align="center", gap="2",
            )
        ),
        rx.table.cell(user_badge(user.is_admin)),
        rx.table.cell(rx.text(user.atendente_nome, size="2", color="#64748B")),
        rx.table.cell(user_status_badge(user.ativo)),
        rx.table.cell(
            rx.flex(
                rx.icon_button(
                    rx.icon("pencil", size=14),
                    variant="ghost", color_scheme="violet", size="1",
                    on_click=AppState.open_edit_user(user.id),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    variant="ghost", color_scheme="red", size="1",
                    on_click=AppState.confirm_delete_user(user.id),
                ),
                gap="1",
            )
        ),
        style={"_hover": {"background_color": "#F8FAFC"}},
    )


def user_form_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(AppState.editando_usuario, "Editar Usuário", "Novo Usuário")
            ),
            rx.flex(
                rx.flex(
                    rx.text("Nome completo", size="2", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Nome do usuário",
                        value=AppState.user_form_nome,
                        on_change=AppState.set_user_form_nome,
                    ),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("E-mail", size="2", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="email@ecm.com.br",
                        type="email",
                        value=AppState.user_form_email,
                        on_change=AppState.set_user_form_email,
                    ),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text(
                        rx.cond(
                            AppState.editando_usuario,
                            "Nova senha (deixe em branco para manter)",
                            "Senha",
                        ),
                        size="2", weight="medium", color="#374151",
                    ),
                    rx.input(
                        placeholder="••••••••",
                        type="password",
                        value=AppState.user_form_senha,
                        on_change=AppState.set_user_form_senha,
                    ),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("Perfil de acesso", size="2", weight="medium", color="#374151"),
                    rx.select(
                        ["Atendente", "Admin"],
                        value=rx.cond(AppState.user_form_is_admin, "Admin", "Atendente"),
                        on_change=AppState.set_user_form_is_admin,
                        width="100%",
                    ),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("Atendente vinculado", size="2", weight="medium", color="#374151"),
                    rx.text("Define quais avaliações este usuário pode ver", size="1", color="#94A3B8"),
                    rx.select(
                        AppState.atendentes_nomes,
                        placeholder="Selecione o atendente...",
                        value=AppState.user_form_atendente_nome,
                        on_change=AppState.set_user_form_atendente_nome,
                        width="100%",
                    ),
                    direction="column", gap="1",
                ),
                direction="column", gap="4", padding_y="4",
            ),
            rx.flex(
                rx.button(
                    "Cancelar",
                    variant="outline", color_scheme="gray",
                    on_click=AppState.close_user_form(False),
                ),
                rx.button(
                    rx.cond(AppState.editando_usuario, "Salvar alterações", "Criar usuário"),
                    color_scheme="violet",
                    on_click=AppState.save_user,
                ),
                gap="3", justify="end",
            ),
            max_width="480px",
        ),
        open=AppState.show_user_form,
        on_open_change=AppState.close_user_form,
    )


def delete_confirm_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Excluir usuário"),
            rx.text(
                "Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.",
                size="2", color="#64748B",
            ),
            rx.flex(
                rx.button(
                    "Cancelar",
                    variant="outline", color_scheme="gray",
                    on_click=AppState.cancel_delete_user(False),
                ),
                rx.button("Excluir", color_scheme="red", on_click=AppState.delete_user),
                gap="3", justify="end", margin_top="4",
            ),
            max_width="400px",
        ),
        open=AppState.show_delete_confirm,
        on_open_change=AppState.cancel_delete_user,
    )




def save_button() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.icon("save", size=14), "Salvar Configurações",
            color_scheme="violet", size="3",
            on_click=AppState.salvar_configuracoes,
        ),
        justify="end",
    )


def tab_usuarios() -> rx.Component:
    return rx.flex(
        config_section(
            "Gerenciamento de Usuários",
            "Adicione, edite ou remova usuários. Admins visualizam todos os dados; atendentes veem apenas o próprio desempenho.",
            rx.flex(
                rx.flex(
                    rx.flex(flex="1"),
                    rx.button(
                        rx.icon("plus", size=14), "Novo usuário",
                        color_scheme="violet", size="2",
                        on_click=AppState.open_add_user,
                    ),
                    justify="end", margin_bottom="3",
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Usuário"),
                            rx.table.column_header_cell("Perfil"),
                            rx.table.column_header_cell("Atendente vinculado"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Ações"),
                        ),
                        background_color="#F8FAFC",
                    ),
                    rx.table.body(rx.foreach(AppState.usuarios, user_row)),
                    width="100%", variant="ghost",
                ),
                direction="column",
            ),
        ),
        direction="column", gap="5",
    )


def tab_avaliacao() -> rx.Component:
    return rx.flex(
        config_section(
            "Limites de Nota",
            "Define os limiares para classificação de atendimentos por qualidade.",
            rx.flex(
                rx.flex(
                    rx.text("Nota mínima — Excelente", size="2", weight="medium", color="#374151"),
                    rx.flex(
                        rx.input(
                            placeholder="8.0",
                            value=AppState.config_nota_excelente,
                            on_change=AppState.set_config_nota_excelente,
                            width="100px",
                        ),
                        rx.text("de 0 a 10", size="1", color="#94A3B8"),
                        align="center", gap="2",
                    ),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Nota mínima — Bom", size="2", weight="medium", color="#374151"),
                    rx.flex(
                        rx.input(
                            placeholder="6.0",
                            value=AppState.config_nota_bom,
                            on_change=AppState.set_config_nota_bom,
                            width="100px",
                        ),
                        rx.text("de 0 a 10", size="1", color="#94A3B8"),
                        align="center", gap="2",
                    ),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.text("Nota mínima — Regular", size="2", weight="medium", color="#374151"),
                    rx.flex(
                        rx.input(
                            placeholder="4.0",
                            value=AppState.config_nota_regular,
                            on_change=AppState.set_config_nota_regular,
                            width="100px",
                        ),
                        rx.text("de 0 a 10", size="1", color="#94A3B8"),
                        align="center", gap="2",
                    ),
                    justify="between", align="center",
                ),
                direction="column", gap="4",
            ),
        ),
        config_section(
            "Etiqueta de Revisão",
            "Badge exibido nas avaliações que tiveram nota revisada ou justificativa preenchida.",
            rx.flex(
                rx.flex(
                    rx.text("Nome da etiqueta", size="2", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Ex: Revisado",
                        value=AppState.config_etiqueta_revisao_nome,
                        on_change=AppState.set_config_etiqueta_revisao_nome,
                        width="200px",
                    ),
                    justify="between", align="center",
                ),
                rx.flex(
                    rx.flex(
                        rx.text("Cor da etiqueta", size="2", weight="medium", color="#374151"),
                        rx.badge(
                            rx.icon("pencil-line", size=10),
                            AppState.config_etiqueta_revisao_nome,
                            color_scheme=AppState.config_etiqueta_revisao_cor,
                            variant="soft",
                            style={"gap": "4px"},
                        ),
                        align="center", gap="3",
                    ),
                    rx.flex(
                        # Row 1: warm tones
                        _swatch("red",     "#EF4444"),
                        _swatch("tomato",  "#E54D2E"),
                        _swatch("orange",  "#F97316"),
                        _swatch("amber",   "#F59E0B"),
                        _swatch("yellow",  "#EAB308"),
                        # Row 2: greens/blues
                        _swatch("lime",    "#84CC16"),
                        _swatch("green",   "#22C55E"),
                        _swatch("teal",    "#14B8A6"),
                        _swatch("cyan",    "#06B6D4"),
                        _swatch("sky",     "#0EA5E9"),
                        # Row 3: purples/pinks
                        _swatch("blue",    "#3B82F6"),
                        _swatch("indigo",  "#6366F1"),
                        _swatch("violet",  "#7700FF"),
                        _swatch("purple",  "#9333EA"),
                        _swatch("pink",    "#EC4899"),
                        # Row 4: neutrals
                        _swatch("crimson", "#DB2777"),
                        _swatch("brown",   "#B45309"),
                        _swatch("bronze",  "#8B6351"),
                        _swatch("gold",    "#B7860B"),
                        _swatch("gray",    "#94A3B8"),
                        flex_wrap="wrap",
                        gap="2",
                        max_width="200px",
                    ),
                    justify="between", align="start",
                ),
                direction="column", gap="4",
            ),
        ),
        save_button(),
        direction="column", gap="5",
    )




def tab_prompt_ia() -> rx.Component:
    return rx.flex(
        config_section(
            "Prompt de Avaliação da IA",
            "Texto enviado ao modelo para avaliar cada atendimento. O marcador {relatorio} é obrigatório — é onde o histórico da conversa é inserido.",
            rx.flex(
                # Aviso de {relatorio} ausente — só aparece enquanto editando
                rx.cond(
                    AppState.config_prompt_editando & ~AppState.config_prompt_avaliacao.contains("{relatorio}"),
                    rx.flex(
                        rx.icon("triangle-alert", size=16, color="#DC2626"),
                        rx.text(
                            "O marcador {relatorio} está ausente. O prompt não pode ser salvo sem ele.",
                            size="2", color="#DC2626",
                        ),
                        align="center", gap="2",
                        padding="12px 16px",
                        border_radius="8px",
                        background_color="#FEF2F2",
                        border="1px solid #FECACA",
                    ),
                    rx.box(),
                ),
                # Textarea — read-only quando não está editando
                rx.text_area(
                    value=AppState.config_prompt_avaliacao,
                    on_change=AppState.set_config_prompt_avaliacao,
                    rows="28",
                    read_only=~AppState.config_prompt_editando,
                    style={
                        "font_family": "monospace",
                        "font_size": "13px",
                        "line_height": "1.6",
                        "resize": "vertical",
                        "width": "100%",
                        "border": "1px solid #E2E8F0",
                        "border_radius": "8px",
                        "padding": "12px",
                        "background": rx.cond(AppState.config_prompt_editando, "white", "#F8FAFC"),
                        "color": "#1E293B",
                        "cursor": rx.cond(AppState.config_prompt_editando, "text", "default"),
                        "_focus": {"border_color": "#7700FF", "outline": "none"},
                        "transition": "background 0.2s ease",
                    },
                ),
                # Botões — mudam conforme o modo
                rx.cond(
                    AppState.config_prompt_editando,
                    # Modo edição: Restaurar padrão | Cancelar | Salvar
                    rx.flex(
                        rx.button(
                            rx.icon("rotate-ccw", size=14), "Restaurar padrão",
                            variant="ghost", color_scheme="gray", size="2",
                            on_click=AppState.restaurar_prompt_padrao,
                        ),
                        rx.flex(
                            rx.button(
                                "Cancelar",
                                variant="outline", color_scheme="gray", size="2",
                                on_click=AppState.cancelar_edicao_prompt,
                            ),
                            rx.button(
                                rx.icon("save", size=14), "Salvar Prompt",
                                color_scheme="violet", size="2",
                                on_click=AppState.salvar_prompt,
                                disabled=~AppState.config_prompt_avaliacao.contains("{relatorio}"),
                            ),
                            gap="2",
                        ),
                        justify="between", align="center",
                    ),
                    # Modo leitura: apenas o botão Editar
                    rx.flex(
                        rx.button(
                            rx.icon("pencil", size=14), "Editar Prompt",
                            variant="outline", color_scheme="violet", size="2",
                            on_click=AppState.iniciar_edicao_prompt,
                        ),
                        justify="end",
                    ),
                ),
                direction="column", gap="3",
            ),
        ),
        direction="column", gap="5",
    )


def configuracoes_content() -> rx.Component:
    return rx.flex(
        user_form_dialog(),
        delete_confirm_dialog(),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Usuários", value="usuarios"),
                rx.tabs.trigger("Avaliação", value="avaliacao"),
                rx.tabs.trigger("Prompt IA", value="prompt_ia"),
            ),
            rx.tabs.content(tab_usuarios(), value="usuarios", padding_top="5"),
            rx.tabs.content(tab_avaliacao(), value="avaliacao", padding_top="5"),
            rx.tabs.content(tab_prompt_ia(), value="prompt_ia", padding_top="5"),
            value=AppState.config_aba,
            on_change=AppState.set_config_aba,
            width="100%",
        ),
        direction="column",
        gap="4",
        width="100%",
    )


@rx.page(route="/configuracoes", title="Configurações — ECM", on_load=AppState.verificar_auth_admin)
def configuracoes() -> rx.Component:
    return page_layout(configuracoes_content(), "Configurações")
