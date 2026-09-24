"""Colour palettes, typography, and Windows light/dark detection."""

from __future__ import annotations

from dataclasses import dataclass, field

# Claude's terracotta, used as the single accent so the tool reads as part of
# the same family as the thing it measures.
ACCENT = "#d97757"


@dataclass(frozen=True)
class Palette:
    name: str
    bg: str
    surface: str
    surface_alt: str
    border: str
    text: str
    text_muted: str
    text_faint: str
    track: str
    accent: str
    ok: str
    warn: str
    crit: str
    idle: str
    row_alt: str
    selection: str
    shadow: bool


LIGHT = Palette(
    name="light",
    bg="#f4f5f7",
    surface="#ffffff",
    surface_alt="#fafbfc",
    border="#e4e7ec",
    text="#101828",
    text_muted="#667085",
    text_faint="#98a2b3",
    track="#eaedf1",
    accent=ACCENT,
    ok="#2e9e5b",
    warn="#d9822b",
    crit="#c8402f",
    idle="#98a2b3",
    row_alt="#fafbfc",
    selection="#fdeee8",
    shadow=True,
)

DARK = Palette(
    name="dark",
    bg="#141619",
    surface="#1c1f24",
    surface_alt="#22262c",
    border="#2c313a",
    text="#e9ebee",
    text_muted="#98a1ae",
    text_faint="#6d7683",
    track="#2a2f37",
    accent=ACCENT,
    ok="#3fb571",
    warn="#e0913c",
    crit="#e05c48",
    idle="#6d7683",
    row_alt="#1f2329",
    selection="#3a2a24",
    shadow=False,
)

PALETTES = {"light": LIGHT, "dark": DARK}

# Stable per-model accent colours for table dots and legends. Picked to stay
# distinguishable on both palettes.
MODEL_COLORS = (
    "#d97757",
    "#4f8ff7",
    "#3fb571",
    "#b47ae0",
    "#e0a93c",
    "#3fb9c4",
    "#e06a9a",
    "#8a94a6",
)

# Ordered so the models seen most often get the most distinctive colours.
_MODEL_ORDER = (
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-haiku-4-5",
    "claude-opus-4-8",
    "claude-fable-5",
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-mythos-5",
)


def model_color(model: str) -> str:
    """A stable colour for a model id, known ones first then hashed."""
    if model in _MODEL_ORDER:
        return MODEL_COLORS[_MODEL_ORDER.index(model) % len(MODEL_COLORS)]
    return MODEL_COLORS[hash(model) % len(MODEL_COLORS)]


def system_prefers_dark() -> bool:
    """Read the Windows app-theme preference. Defaults to light."""
    try:
        import winreg
    except ImportError:
        return False
    try:
        key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
            value, _kind = winreg.QueryValueEx(handle, "AppsUseLightTheme")
        return int(value) == 0
    except (OSError, ValueError, TypeError):
        return False


def resolve_palette(mode: str = "auto") -> Palette:
    if mode in PALETTES:
        return PALETTES[mode]
    return DARK if system_prefers_dark() else LIGHT


# --------------------------------------------------------------------- fonts

_FAMILY_CANDIDATES = (
    "Segoe UI Variable Text",
    "Segoe UI",
    "Selawik",
    "Tahoma",
)
_DISPLAY_CANDIDATES = (
    "Segoe UI Variable Display",
    "Segoe UI Semibold",
    "Segoe UI",
    "Tahoma",
)


@dataclass
class Fonts:
    """Resolved font tuples. Needs a live Tk root to query families."""

    family: str = "Segoe UI"
    display: str = "Segoe UI"

    body: tuple = field(init=False)
    body_bold: tuple = field(init=False)
    small: tuple = field(init=False)
    small_bold: tuple = field(init=False)
    tiny_caps: tuple = field(init=False)
    heading: tuple = field(init=False)
    metric: tuple = field(init=False)
    metric_lg: tuple = field(init=False)
    donut: tuple = field(init=False)

    def __post_init__(self) -> None:
        self.body = (self.family, 9)
        self.body_bold = (self.family, 9, "bold")
        self.small = (self.family, 8)
        self.small_bold = (self.family, 8, "bold")
        self.tiny_caps = (self.family, 7, "bold")
        self.heading = (self.display, 12, "bold")
        self.metric = (self.display, 15, "bold")
        self.metric_lg = (self.display, 19, "bold")
        self.donut = (self.display, 20, "bold")


def resolve_fonts(root) -> Fonts:
    """Pick the best available families for this machine."""
    try:
        from tkinter import font as tkfont

        available = set(tkfont.families(root))
    except Exception:
        available = set()

    def pick(candidates: tuple[str, ...], fallback: str) -> str:
        for name in candidates:
            if name in available:
                return name
        return fallback

    return Fonts(
        family=pick(_FAMILY_CANDIDATES, "Segoe UI"),
        display=pick(_DISPLAY_CANDIDATES, "Segoe UI"),
    )


__all__ = [
    "ACCENT",
    "DARK",
    "LIGHT",
    "MODEL_COLORS",
    "PALETTES",
    "Fonts",
    "Palette",
    "model_color",
    "resolve_fonts",
    "resolve_palette",
    "system_prefers_dark",
]
