import reflex as rx
from ecm_avaliacoes.components import page_layout
from ecm_avaliacoes.state import AppState
from ecm_avaliacoes.state.state import AvaliacaoItem, MensagemItem


def nota_color(nota: float) -> rx.Var:
    return rx.cond(nota >= 8, "#22C55E", rx.cond(nota >= 6, "#7700FF", rx.cond(nota >= 4, "#F59E0B", "#EF4444")))


def table_row(av: AvaliacaoItem) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.text(av.protocolo, size="1", color="#64748B", font_family="monospace"),
                rx.text(av.data_atendimento, size="1", color="#94A3B8"),
                direction="column",
                gap="0",
            )
        ),
        rx.table.cell(rx.text(av.cliente, size="2", weight="medium", color="#1E293B")),
        rx.table.cell(
            rx.cond(
                av.responsavel == "Não identificado",
                rx.flex(
                    rx.icon("user-x", size=14, color="#F59E0B"),
                    rx.text(av.responsavel, size="2", color="#F59E0B", weight="medium"),
                    align="center", gap="2",
                ),
                rx.flex(
                    rx.avatar(fallback=av.responsavel[:2], size="1", color_scheme="violet"),
                    rx.text(av.responsavel, size="2", color="#374151"),
                    align="center", gap="2",
                ),
            )
        ),
        rx.table.cell(
            rx.flex(
                rx.text(av.nota, size="2", color=nota_color(av.nota)),
                rx.text("/10", size="1", color="#94A3B8"),
                align="baseline",
                gap="1",
            )
        ),
        rx.table.cell(
            rx.flex(
                rx.match(
                    av.status,
                    ("Excelente", rx.badge("Excelente", color_scheme="green", variant="soft")),
                    ("Bom", rx.badge("Bom", color_scheme="violet", variant="soft")),
                    ("Regular", rx.badge("Regular", color_scheme="orange", variant="soft")),
                    ("Crítico", rx.badge("Crítico", color_scheme="red", variant="soft")),
                    rx.badge(av.status, variant="soft"),
                ),
                rx.cond(
                    av.justificativa_revisao != "",
                    rx.tooltip(
                        rx.badge(
                            rx.icon("pencil-line", size=10),
                            AppState.config_etiqueta_revisao_nome,
                            color_scheme=AppState.config_etiqueta_revisao_cor,
                            variant="soft",
                            style={"gap": "4px"},
                        ),
                        content="Nota revisada: " + av.justificativa_revisao,
                    ),
                    rx.box(),
                ),
                rx.cond(
                    av.conferido,
                    rx.tooltip(
                        rx.icon("circle-check", size=14, color="#22C55E"),
                        content="Atestado por " + av.conferido_por,
                    ),
                    rx.box(),
                ),
                align="center",
                gap="2",
            )
        ),
        rx.table.cell(rx.text(av.tempo_formatado, size="2", color="#64748B")),
        rx.table.cell(
            rx.icon_button(
                rx.icon("eye", size=15),
                variant="ghost",
                color_scheme="violet",
                size="1",
                on_click=AppState.open_avaliacao(av.id),
            )
        ),
        style={"_hover": {"background_color": "#F8FAFC"}, "cursor": "pointer"},
        on_click=AppState.open_avaliacao(av.id),
    )


def _flabel(text: str) -> rx.Component:
    return rx.text(text, size="1", color="#64748B", weight="medium")


def filters_bar() -> rx.Component:
    return rx.flex(
        rx.flex(
            _flabel("Buscar"),
            rx.input(
                rx.input.slot(rx.icon("search", size=15, color="#94A3B8")),
                placeholder="Protocolo, cliente ou atendente...",
                value=AppState.search_query,
                on_change=AppState.set_search,
                width="300px",
                style={"background_color": "white"},
            ),
            direction="column", gap="1",
        ),
        rx.flex(
            _flabel("Mês"),
            rx.select(
                AppState.meses_com_todos,
                value=AppState.filter_mes_display,
                on_change=AppState.set_filter_mes,
                width="130px",
            ),
            direction="column", gap="1",
        ),
        rx.flex(
            _flabel("Status"),
            rx.select(
                ["Todos", "Excelente", "Bom", "Regular", "Crítico"],
                value=AppState.filter_status_display,
                on_change=AppState.set_filter_status,
                width="150px",
            ),
            direction="column", gap="1",
        ),
        rx.flex(
            _flabel("Conferência"),
            rx.select(
                ["Todos", "Atestado", "Pendente"],
                value=AppState.filter_conferido_display,
                on_change=AppState.set_filter_conferido,
                width="140px",
            ),
            direction="column", gap="1",
        ),
        rx.flex(
            _flabel("Revisão"),
            rx.select(
                ["Todos", "Revisados", "Sem revisão"],
                value=AppState.filter_revisado_display,
                on_change=AppState.set_filter_revisado,
                width="140px",
            ),
            direction="column", gap="1",
        ),
        rx.cond(
            AppState.current_user_is_admin,
            rx.flex(
                _flabel("Atendente"),
                rx.select(
                    AppState.atendentes_com_todos,
                    value=AppState.filter_responsavel_display,
                    on_change=AppState.set_filter_responsavel,
                    width="190px",
                ),
                direction="column", gap="1",
            ),
            rx.box(),
        ),
        rx.flex(
            rx.box(height="16px"),
            rx.button(
                rx.icon("x", size=14), "Limpar",
                variant="ghost", color_scheme="gray", size="2",
                on_click=AppState.clear_filters,
            ),
            direction="column", gap="1",
        ),
        rx.flex(flex="1"),
        rx.flex(
            rx.box(height="16px"),
            rx.button(
                rx.icon("download", size=14), "Exportar CSV",
                variant="outline", color_scheme="violet", size="2",
            ),
            direction="column", gap="1",
        ),
        align="end",
        gap="3",
        padding="16px 0",
        flex_wrap="wrap",
    )


def mensagem_bubble(msg: MensagemItem) -> rx.Component:
    return rx.match(
        msg.tipo,
        # Sistema — linha central discreta
        ("sistema",
            rx.flex(
                rx.flex(
                    rx.icon("info", size=10, color="#94A3B8"),
                    rx.text(msg.conteudo, size="1", color="#94A3B8"),
                    align="center", gap="2",
                    padding="4px 12px",
                    background="#F8FAFC",
                    border_radius="20px",
                    border="1px solid #E2E8F0",
                ),
                justify="center",
                padding_y="6px",
                width="100%",
            )
        ),
        # BOT — balão azul à esquerda
        ("bot",
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.icon("bot", size=11, color="white"),
                        width="26px", height="26px", flex_shrink="0",
                        background="#3B82F6",
                        border_radius="50%",
                        align="center", justify="center",
                    ),
                    rx.flex(
                        rx.text(msg.conteudo, size="2", color="#1E293B", line_height="1.6"),
                        rx.text(msg.hora, size="1", color="#93C5FD", margin_top="4px"),
                        direction="column",
                        padding="10px 14px",
                        background="#EFF6FF",
                        border="1px solid #BFDBFE",
                        border_radius="4px 12px 12px 12px",
                        max_width="78%",
                    ),
                    align="start", gap="2",
                ),
                width="100%",
                padding_y="3px",
            )
        ),
        # Cliente — balão roxo à direita
        ("cliente",
            rx.flex(
                rx.flex(
                    rx.flex(
                        rx.text(msg.conteudo, size="2", color="white", line_height="1.6"),
                        rx.text(msg.hora, size="1", color="rgba(255,255,255,0.6)", margin_top="4px"),
                        direction="column",
                        padding="10px 14px",
                        background="#7700FF",
                        border_radius="12px 4px 12px 12px",
                        max_width="78%",
                    ),
                    rx.avatar(fallback=msg.autor[:2], size="1", color_scheme="gray"),
                    align="start", gap="2",
                ),
                justify="end",
                width="100%",
                padding_y="3px",
            )
        ),
        # Atendente — balão branco à esquerda (default)
        rx.flex(
            rx.flex(
                rx.avatar(fallback=msg.autor[:2], size="1", color_scheme="violet"),
                rx.flex(
                    rx.text(msg.conteudo, size="2", color="#1E293B", line_height="1.6"),
                    rx.flex(
                        rx.text(msg.autor, size="1", color="#7700FF", weight="medium"),
                        rx.text("·", size="1", color="#CBD5E1"),
                        rx.text(msg.hora, size="1", color="#94A3B8"),
                        align="center", gap="1",
                    ),
                    direction="column",
                    padding="10px 14px",
                    background="white",
                    border="1px solid #E2E8F0",
                    border_radius="4px 12px 12px 12px",
                    max_width="78%",
                ),
                align="start", gap="2",
            ),
            width="100%",
            padding_y="3px",
        ),
    )


def tab_informacoes(av: AvaliacaoItem) -> rx.Component:
    return rx.flex(
        # Nota em destaque
        rx.flex(
            rx.flex(
                rx.flex(
                    rx.heading(av.nota, size="9", color="#7700FF", weight="bold"),
                    rx.text("/10", size="4", color="#94A3B8", weight="medium"),
                    align="baseline", gap="1",
                ),
                rx.text(
                    "Nota Final", size="1", color="#94A3B8", weight="medium",
                    text_transform="uppercase", letter_spacing="0.08em",
                ),
                direction="column", align="center", gap="1",
            ),
            rx.separator(orientation="vertical", size="3"),
            rx.grid(
                rx.flex(
                    rx.text("Atendente", size="1", color="#94A3B8", weight="medium"),
                    rx.text(av.responsavel, size="2", color="#1E293B", weight="medium"),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("Data", size="1", color="#94A3B8", weight="medium"),
                    rx.text(av.data_atendimento, size="2", color="#1E293B"),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("Início", size="1", color="#94A3B8", weight="medium"),
                    rx.text(av.hora_inicio, size="2", color="#1E293B"),
                    direction="column", gap="1",
                ),
                rx.flex(
                    rx.text("Duração", size="1", color="#94A3B8", weight="medium"),
                    rx.text(av.tempo_formatado, size="2", color="#1E293B"),
                    direction="column", gap="1",
                ),
                columns="2", gap="4", flex="1",
            ),
            align="center", gap="5",
            padding="16px 0",
            border_bottom="1px solid #F1F5F9",
        ),
        # Pontos Críticos
        rx.flex(
            rx.flex(
                rx.icon("triangle-alert", size=15, color="#F59E0B"),
                rx.text("Pontos Críticos", size="2", color="#1E293B", weight="medium"),
                align="center", gap="2",
            ),
            rx.box(
                rx.text(av.pontos_criticos, size="2", color="#374151", line_height="1.6"),
                background="#FFFBEB",
                border="1px solid #FDE68A",
                border_radius="8px",
                padding="12px 14px",
            ),
            direction="column", gap="2",
            padding_top="14px",
        ),
        # Feedback Final
        rx.flex(
            rx.flex(
                rx.icon("message-square", size=15, color="#22C55E"),
                rx.text("Feedback Final", size="2", color="#1E293B", weight="medium"),
                align="center", gap="2",
            ),
            rx.box(
                rx.text(av.feedback_final, size="2", color="#374151", line_height="1.6"),
                background="#F0FDF4",
                border="1px solid #BBF7D0",
                border_radius="8px",
                padding="12px 14px",
            ),
            direction="column", gap="2",
            padding_top="10px",
        ),
        # Justificativa de revisão aplicada
        rx.cond(
            av.justificativa_revisao != "",
            rx.flex(
                rx.flex(
                    rx.icon("pencil-line", size=15, color="#7700FF"),
                    rx.text("Revisão aplicada", size="2", color="#1E293B", weight="medium"),
                    align="center", gap="2",
                ),
                rx.box(
                    rx.text(av.justificativa_revisao, size="2", color="#374151", line_height="1.6"),
                    background="#F3EEFF",
                    border="1px solid #E4D0FF",
                    border_radius="8px",
                    padding="12px 14px",
                ),
                direction="column", gap="2",
                padding_top="10px",
            ),
            rx.box(),
        ),
        # Revisão de nota (inline)
        rx.cond(
            AppState.editando_nota,
            rx.flex(
                rx.flex(
                    rx.icon("pencil", size=15, color="#7700FF"),
                    rx.text("Revisão de Nota", size="2", color="#1E293B", weight="medium"),
                    align="center", gap="2",
                ),
                rx.flex(
                    rx.flex(
                        rx.text("Nova nota (0 – 10)", size="1", color="#64748B"),
                        rx.input(
                            value=AppState.revisar_nova_nota,
                            on_change=AppState.set_revisar_nova_nota,
                            placeholder="Ex: 7.5",
                            type="number",
                            min="0", max="10", step="0.1",
                            width="140px",
                            size="2",
                        ),
                        direction="column", gap="1",
                    ),
                    width="100%",
                ),
                rx.flex(
                    rx.text("Justificativa", size="1", color="#64748B"),
                    rx.text_area(
                        value=AppState.revisar_justificativa,
                        on_change=AppState.set_revisar_justificativa,
                        placeholder="Descreva o motivo da revisão...",
                        rows="3",
                        width="100%",
                        resize="none",
                    ),
                    direction="column", gap="1",
                    width="100%",
                ),
                direction="column", gap="3",
                padding="16px",
                background="#F3EEFF",
                border="1px solid #E4D0FF",
                border_radius="8px",
                margin_top="14px",
                width="100%",
            ),
            rx.box(),
        ),
        direction="column",
    )


def tab_historico() -> rx.Component:
    total = AppState.historico_da_conversa.length()
    return rx.cond(
        AppState.historico_loading,
        rx.flex(
            rx.spinner(size="3", color_scheme="violet"),
            rx.text("Carregando histórico da conversa...", size="2", color="#94A3B8"),
            direction="column", align="center", gap="3",
            padding="48px 0",
        ),
        rx.cond(
            total == 0,
            rx.flex(
                rx.icon("message-square-off", size=36, color="#CBD5E1"),
                rx.text("Histórico não disponível para esta avaliação.", size="2", color="#94A3B8"),
                rx.text("Apenas avaliações processadas após a atualização do sistema possuem histórico.", size="1", color="#CBD5E1", text_align="center"),
                direction="column", align="center", gap="2",
                padding="40px 0",
            ),
            rx.flex(
                # Cabeçalho da conversa
                rx.flex(
                    rx.icon("message-circle", size=14, color="#7700FF"),
                    rx.text(total, size="2", color="#7700FF", weight="medium"),
                    rx.text("mensagens", size="2", color="#94A3B8"),
                    align="center", gap="2",
                    padding_bottom="12px",
                    border_bottom="1px solid #F1F5F9",
                    margin_bottom="4px",
                ),
                # Mensagens
                rx.flex(
                    rx.foreach(AppState.historico_da_conversa, mensagem_bubble),
                    direction="column",
                    gap="1",
                    overflow_y="auto",
                    max_height="360px",
                    padding_right="4px",
                    padding_y="4px",
                ),
                direction="column",
            ),
        ),
    )


def desconsiderar_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Desconsiderar avaliação"),
            rx.text(
                "Este atendimento será removido permanentemente do banco de dados e não contabilizará no desempenho do atendente.",
                size="2", color="#64748B",
            ),
            rx.flex(
                rx.text("Protocolo:", size="2", weight="medium", color="#374151"),
                rx.text(AppState.selected_avaliacao.protocolo, size="2", color="#7700FF", font_family="monospace"),
                gap="2", align="center", margin_top="3",
            ),
            rx.flex(
                rx.button(
                    "Cancelar", variant="outline", color_scheme="gray",
                    on_click=AppState.fechar_desconsiderar,
                ),
                rx.button(
                    rx.icon("trash-2", size=14), "Sim, remover",
                    color_scheme="red",
                    on_click=AppState.desconsiderar_avaliacao,
                ),
                gap="3", justify="end", margin_top="5",
            ),
            max_width="420px",
        ),
        open=AppState.show_desconsiderar_confirm,
        on_open_change=AppState.cancelar_desconsiderar,
    )


def vincular_atendente_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Vincular Atendente"),
            rx.text(
                "Selecione o atendente responsável por este atendimento. A alteração será salva no banco de dados e os relatórios serão atualizados.",
                size="2", color="#64748B",
            ),
            rx.flex(
                rx.text("Protocolo:", size="2", weight="medium", color="#374151"),
                rx.text(AppState.selected_avaliacao.protocolo, size="2", color="#7700FF", font_family="monospace"),
                gap="2", align="center", margin_top="3",
            ),
            rx.flex(
                rx.text("Atendente", size="1", color="#64748B", weight="medium"),
                rx.select(
                    AppState.atendentes_identificados,
                    placeholder="Selecione um atendente...",
                    value=AppState.vincular_atendente_selecionado,
                    on_change=AppState.set_vincular_atendente_selecionado,
                    width="100%",
                ),
                direction="column", gap="1", margin_top="4", width="100%",
            ),
            rx.flex(
                rx.button(
                    "Cancelar", variant="outline", color_scheme="gray",
                    on_click=AppState.fechar_vincular_atendente,
                ),
                rx.button(
                    rx.icon("user-check", size=14), "Confirmar vínculo",
                    color_scheme="violet",
                    on_click=AppState.confirmar_vincular_atendente,
                ),
                gap="3", justify="end", margin_top="5",
            ),
            max_width="420px",
        ),
        open=AppState.show_vincular_atendente,
        on_open_change=AppState.close_vincular_atendente,
    )


def avaliacao_modal() -> rx.Component:
    av = AppState.selected_avaliacao
    return rx.dialog.root(
        rx.dialog.content(
            # Cabeçalho com gradiente
            rx.box(
                rx.flex(
                    rx.flex(
                        rx.flex(
                            rx.icon("clipboard-list", size=18, color="white"),
                            width="36px", height="36px",
                            background="linear-gradient(135deg, #7700FF, #00D4C8)",
                            border_radius="10px",
                            align="center", justify="center",
                            flex_shrink="0",
                        ),
                        rx.flex(
                            rx.text(av.protocolo, size="1", color="rgba(255,255,255,0.7)", font_family="monospace"),
                            rx.heading(av.cliente, size="4", color="white"),
                            direction="column", gap="0",
                        ),
                        align="center", gap="3",
                    ),
                    rx.flex(
                        rx.match(
                            av.status,
                            ("Excelente", rx.badge("Excelente", color_scheme="green", variant="solid", size="2")),
                            ("Bom", rx.badge("Bom", color_scheme="violet", variant="solid", size="2")),
                            ("Regular", rx.badge("Regular", color_scheme="orange", variant="solid", size="2")),
                            ("Crítico", rx.badge("Crítico", color_scheme="red", variant="solid", size="2")),
                            rx.badge("—"),
                        ),
                        rx.dialog.close(
                            rx.icon_button(
                                rx.icon("x", size=16),
                                variant="ghost",
                                size="2",
                                style={"color": "rgba(255,255,255,0.8)", "_hover": {"background": "rgba(255,255,255,0.15)"}},
                            ),
                        ),
                        align="center", gap="3",
                    ),
                    justify="between", align="center",
                ),
                background="linear-gradient(135deg, #7700FF 0%, #5500CC 100%)",
                padding="20px 24px",
                border_radius="12px 12px 0 0",
                margin="-24px -24px 0 -24px",
            ),
            # Abas
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Informações", value="informacoes"),
                    rx.tabs.trigger(
                        rx.flex(
                            "Histórico",
                            rx.cond(
                                AppState.historico_loading,
                                rx.spinner(size="1"),
                                rx.cond(
                                    AppState.historico_da_conversa.length() > 0,
                                    rx.badge(
                                        AppState.historico_da_conversa.length(),
                                        color_scheme="violet", variant="soft", size="1",
                                    ),
                                    rx.box(),
                                ),
                            ),
                            align="center", gap="2",
                        ),
                        value="historico",
                    ),
                    margin_top="4",
                    margin_bottom="2",
                ),
                rx.tabs.content(
                    tab_informacoes(av),
                    value="informacoes",
                    padding_top="0",
                ),
                rx.tabs.content(
                    tab_historico(),
                    value="historico",
                    padding_top="4",
                ),
                value=AppState.drawer_tab,
                on_change=AppState.set_drawer_tab,
                width="100%",
            ),
            # Ações
            rx.cond(
                AppState.editando_nota,
                rx.flex(
                    rx.button(
                        "Cancelar",
                        variant="soft", color_scheme="gray", size="2",
                        on_click=AppState.cancelar_revisao,
                    ),
                    rx.button(
                        rx.icon("save", size=14), "Salvar Revisão",
                        color_scheme="violet", size="2",
                        on_click=AppState.salvar_revisao_nota,
                    ),
                    gap="3", justify="end",
                    padding_top="20px", border_top="1px solid #F1F5F9", margin_top="16px",
                ),
                rx.flex(
                    rx.cond(
                        AppState.current_user_is_admin & AppState.selected_precisa_conferencia,
                        rx.cond(
                            AppState.selected_avaliacao.conferido,
                            rx.flex(
                                rx.icon("circle-check", size=14, color="#22C55E"),
                                rx.text(
                                    "Atestado por " + AppState.selected_avaliacao.conferido_por,
                                    size="2", color="#22C55E", weight="medium",
                                ),
                                align="center", gap="2",
                                padding="6px 12px",
                                background="#F0FDF4",
                                border="1px solid #BBF7D0",
                                border_radius="6px",
                            ),
                            rx.button(
                                rx.icon("shield-check", size=14), "Atestar",
                                variant="outline", color_scheme="green", size="2",
                                on_click=AppState.marcar_conferido,
                            ),
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        AppState.current_user_is_admin & AppState.selected_e_nao_identificado,
                        rx.button(
                            rx.icon("user-plus", size=14), "Vincular Atendente",
                            variant="outline", color_scheme="orange", size="2",
                            on_click=AppState.open_vincular_atendente,
                        ),
                        rx.box(),
                    ),
                    rx.flex(flex="1"),
                    rx.cond(
                        AppState.current_user_is_admin,
                        rx.button(
                            rx.icon("pencil", size=14), "Revisar Nota",
                            variant="outline", color_scheme="violet", size="2",
                            on_click=AppState.open_revisar_nota,
                        ),
                        rx.box(),
                    ),
                    rx.button(
                        rx.icon("circle-x", size=14), "Desconsiderar",
                        variant="outline", color_scheme="red", size="2",
                        on_click=AppState.abrir_confirmar_desconsiderar,
                    ),
                    rx.dialog.close(
                        rx.button("Fechar", variant="soft", color_scheme="gray", size="2"),
                    ),
                    gap="3", align="center",
                    padding_top="20px", border_top="1px solid #F1F5F9", margin_top="16px",
                ),
            ),
            max_width="640px",
            style={"border_radius": "12px", "padding": "24px"},
        ),
        open=AppState.show_drawer,
        on_open_change=AppState.close_drawer,
    )


def avaliacoes_content() -> rx.Component:
    return rx.flex(
        filters_bar(),
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Protocolo / Data"),
                        rx.table.column_header_cell("Cliente"),
                        rx.table.column_header_cell("Atendente"),
                        rx.table.column_header_cell("Nota"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Duração"),
                        rx.table.column_header_cell(""),
                    ),
                    background_color="#F8FAFC",
                ),
                rx.table.body(
                    rx.foreach(AppState.avaliacoes_filtradas, table_row),
                ),
                width="100%",
                variant="ghost",
            ),
            background_color="white",
            border_radius="12px",
            border="1px solid #E2E8F0",
            overflow="hidden",
            padding="0",
        ),
        avaliacao_modal(),
        desconsiderar_dialog(),
        vincular_atendente_dialog(),
        direction="column",
        gap="0",
        width="100%",
    )


@rx.page(route="/avaliacoes", title="Avaliações — ECM", on_load=AppState.verificar_auth)
def avaliacoes() -> rx.Component:
    return page_layout(avaliacoes_content(), "Gestão de Avaliações")
