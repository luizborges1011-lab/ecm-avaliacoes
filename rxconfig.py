import os
import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin
from reflex_components_radix.plugin import RadixThemesPlugin

_railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

config = rx.Config(
    app_name="ecm_avaliacoes",
    api_url=f"https://{_railway_domain}" if _railway_domain else "http://localhost:8000",
    db_url="sqlite:///ecm_avaliacoes.db",
    frontend_port=3001,  # nginx fica na 3000; Reflex frontend na 3001
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
