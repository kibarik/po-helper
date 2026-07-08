from __future__ import annotations
from dataclasses import dataclass, field

_DEFAULT_PALETTE = ["#E4002B", "#2E4B7A", "#0F7A8C", "#2F7D54"]
_DEFAULT_ROLES = {
    "BA": "#B37D0C", "SA": "#B37D0C", "ADR": "#B37D0C",
    "BE": "#2E4B7A", "FE": "#2E4B7A",
    "QA": "#7E56A6", "RELEASE": "#2F8557", "DBA": "#0F7A8C",
}


@dataclass
class Theme:
    accent: str = "#E4002B"
    heading: str = "#1C2333"
    body: str = "#434C60"
    muted: str = "#8B94A6"
    card_bg: str = "#F5F7FB"
    dark_bg: str = "#141A2E"
    subtitle_on_dark: str = "#AEB6CE"
    positive: str = "#2F7D54"
    info: str = "#2E4B7A"
    direction_palette: list[str] = field(default_factory=lambda: list(_DEFAULT_PALETTE))
    role_color_map: dict[str, str] = field(default_factory=lambda: dict(_DEFAULT_ROLES))
    heading_font: str = "Cambria"
    body_font: str = "Calibri"
    slide_w_in: float = 13.333
    slide_h_in: float = 7.5

    def role_color(self, role: str) -> str:
        return self.role_color_map.get(role.strip().upper(), self.body)

    def direction_color(self, index: int) -> str:
        return self.direction_palette[index % len(self.direction_palette)]


_KEYS = {
    "accent_color": "accent", "heading_color": "heading", "body_color": "body",
    "muted_color": "muted", "card_bg": "card_bg",
    "dark_bg": "dark_bg", "subtitle_on_dark": "subtitle_on_dark",
    "positive_color": "positive", "info_color": "info",
    "direction_palette": "direction_palette", "heading_font": "heading_font",
    "body_font": "body_font",
}


def load_theme(present: dict | None = None) -> Theme:
    t = Theme()
    if not present:
        return t
    for src_key, attr in _KEYS.items():
        if present.get(src_key):
            setattr(t, attr, present[src_key])
    if present.get("role_color_map"):
        merged = dict(_DEFAULT_ROLES)
        merged.update({k.upper(): v for k, v in present["role_color_map"].items()})
        t.role_color_map = merged
    return t
