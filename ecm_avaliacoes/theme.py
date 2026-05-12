import reflex as rx

# Brand colors (unchanged)
BRAND_PURPLE = "#7700FF"
BRAND_TEAL = "#00D4C8"
BRAND_GRADIENT = f"linear-gradient(135deg, {BRAND_PURPLE}, {BRAND_TEAL})"

# Page backgrounds
BG_GRADIENT = "linear-gradient(135deg, #0D0221 0%, #0A1628 100%)"
BG_BASE = "#0D0221"

# Glass surfaces
GLASS_BG = "rgba(255,255,255,0.04)"
GLASS_BG_STRONG = "rgba(255,255,255,0.08)"
GLASS_BG_HOVER = "rgba(255,255,255,0.07)"
GLASS_BORDER = "rgba(255,255,255,0.10)"
GLASS_BORDER_ACCENT = "rgba(119,0,255,0.45)"
GLASS_BORDER_TEAL = "rgba(0,212,200,0.35)"

# Text hierarchy (all on dark bg)
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "rgba(255,255,255,0.65)"
TEXT_MUTED = "rgba(255,255,255,0.38)"

# Shadows & glow
CARD_SHADOW = "0 4px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.07)"
CARD_SHADOW_HOVER = "0 8px 40px rgba(119,0,255,0.22), 0 4px 16px rgba(0,0,0,0.5)"
GLOW_PURPLE = "0 0 24px rgba(119,0,255,0.30)"
GLOW_TEAL = "0 0 24px rgba(0,212,200,0.25)"

# Navigation
NAV_BG = "rgba(13,2,33,0.88)"
NAV_BORDER = "rgba(255,255,255,0.08)"

# Accent row hover in tables
TABLE_ROW_HOVER = "rgba(119,0,255,0.08)"
TABLE_HEADER_BG = "rgba(255,255,255,0.04)"


def glass_card(*children, padding: str = "20px", accent: bool = False, **props) -> rx.Component:
    border_color = GLASS_BORDER_ACCENT if accent else GLASS_BORDER
    return rx.box(
        *children,
        background=GLASS_BG,
        border=f"1px solid {border_color}",
        border_radius="14px",
        box_shadow=CARD_SHADOW,
        padding=padding,
        style={
            "backdrop_filter": "blur(16px)",
            "-webkit-backdrop-filter": "blur(16px)",
            "transition": "box-shadow 0.25s ease, border-color 0.25s ease",
            "_hover": {
                "box_shadow": CARD_SHADOW_HOVER,
                "border_color": GLASS_BORDER_ACCENT,
            },
        },
        **props,
    )


def gradient_badge_box(icon: str, size: int = 20) -> rx.Component:
    return rx.flex(
        rx.icon(icon, size=size, color="white"),
        width="44px",
        height="44px",
        min_width="44px",
        background=BRAND_GRADIENT,
        border_radius="12px",
        align="center",
        justify="center",
        box_shadow=GLOW_PURPLE,
    )
