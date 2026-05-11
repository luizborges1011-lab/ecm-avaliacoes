import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin
from reflex_components_radix.plugin import RadixThemesPlugin

config = rx.Config(
    app_name="ecm_avaliacoes",
    db_url="sqlite:///ecm_avaliacoes.db",
    frontend_port=3000,
    backend_port=8000,
    tailwind=None,
    plugins=[
        SitemapPlugin(),
        RadixThemesPlugin(theme=rx.theme(
            appearance="light",
            has_background=True,
            radius="medium",
            accent_color="blue",
            gray_color="slate",
            scaling="95%",
        )),
    ],
)
