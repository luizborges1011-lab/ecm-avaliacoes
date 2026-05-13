import os
import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin
from reflex_components_radix.plugin import RadixThemesPlugin

_railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

# Railway injeta PORT automaticamente (auto-detectado do EXPOSE 3000).
# Frontend e backend rodam na mesma porta em produção (requisito do Reflex).
_port = int(os.getenv("PORT", 3000))

config = rx.Config(
    app_name="ecm_avaliacoes",
    api_url=f"https://{_railway_domain}" if _railway_domain else f"http://localhost:{_port}",
    db_url="sqlite:///ecm_avaliacoes.db",
    frontend_port=_port,
    backend_port=_port,
    tailwind=None,
    show_built_with_reflex=False,
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
