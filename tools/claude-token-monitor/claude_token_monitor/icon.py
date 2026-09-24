"""Render the tray icon.

The notification area gives us roughly 16x16 device pixels, so the icon is drawn
at 4x and downsampled -- Tk and the shell both scale it, and supersampling keeps
the edges clean at every size. It carries exactly one number, how full the
5-hour window is, with colour for the alert level and a progress ring around the
rim so the state still reads when the digits are too small.
"""

from __future__ import annotations

from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

SIZE = 64
SS = 4  # supersampling factor

COLOR_OK = (46, 158, 91, 255)
COLOR_WARN = (217, 130, 43, 255)
COLOR_CRIT = (200, 64, 47, 255)
COLOR_IDLE = (140, 148, 160, 255)
COLOR_TEXT = (255, 255, 255, 255)

_FONT_CANDIDATES = (
    "segoeuib.ttf",  # Segoe UI Bold
    "seguisb.ttf",  # Segoe UI Semibold
    "arialbd.ttf",
    "calibrib.ttf",
    "DejaVuSans-Bold.ttf",
)


def status_color(
    ratio: float,
    warn_pct: float = 0.60,
    crit_pct: float = 0.85,
    has_data: bool = True,
) -> tuple[int, int, int, int]:
    if not has_data:
        return COLOR_IDLE
    if ratio >= crit_pct:
        return COLOR_CRIT
    if ratio >= warn_pct:
        return COLOR_WARN
    return COLOR_OK


@lru_cache(maxsize=32)
def _font(size: int) -> ImageFont.ImageFont:
    for name in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_font(draw: ImageDraw.ImageDraw, text: str, box: int) -> ImageFont.ImageFont:
    """Largest candidate font whose rendering of ``text`` fits ``box``."""
    best = _font(10)
    for size in range(box, 9, -2):
        font = _font(size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        if (right - left) <= box and (bottom - top) <= box:
            return font
        best = font
    return best


def label_for(ratio: float, has_data: bool = True) -> str:
    """Short text for the icon face."""
    if not has_data:
        return "--"
    pct = ratio * 100
    if pct >= 100:
        return "!"
    if pct >= 10:
        return f"{int(pct)}"
    return f"{pct:.0f}"


def _lighten(color: tuple[int, int, int, int], amount: float) -> tuple[int, int, int, int]:
    r, g, b, a = color
    mix = lambda c: int(c + (255 - c) * amount)  # noqa: E731
    return (mix(r), mix(g), mix(b), a)


def render_icon(
    ratio: float,
    *,
    warn_pct: float = 0.60,
    crit_pct: float = 0.85,
    has_data: bool = True,
    size: int = SIZE,
) -> Image.Image:
    """Draw the tray icon for a fill ratio in 0..1."""
    ratio = max(0.0, min(1.5, float(ratio)))
    fill = status_color(ratio, warn_pct, crit_pct, has_data)

    big = size * SS
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # The rim ring is redundancy, not the primary signal -- keep it thin so the
    # digits stay as large as possible. At 16 device pixels the number is the
    # only thing with a chance of being read.
    rim = max(SS, int(big * 0.07))
    margin = rim // 2

    # Progress ring around the rim: visible even when the digits are not.
    ring_box = (margin, margin, big - margin - 1, big - margin - 1)
    draw.arc(ring_box, start=0, end=360, fill=_lighten(fill, 0.62), width=rim)
    if has_data and ratio > 0.005:
        draw.arc(
            ring_box,
            start=-90,
            end=-90 + 360 * min(1.0, ratio),
            fill=_lighten(fill, 0.18),
            width=rim,
        )

    # Solid core carries the colour and hosts the number.
    inset = rim + max(SS // 2, int(big * 0.012))
    draw.ellipse((inset, inset, big - inset - 1, big - inset - 1), fill=fill)

    text = label_for(ratio, has_data)
    font = _fit_font(draw, text, box=int(big * 0.60))
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    x = (big - (right - left)) / 2 - left
    y = (big - (bottom - top)) / 2 - top
    draw.text((x, y), text, font=font, fill=COLOR_TEXT)

    return image.resize((size, size), Image.LANCZOS)


__all__ = ["SIZE", "label_for", "render_icon", "status_color"]
