"""Antialiased chrome rendered with Pillow.

Tk's canvas draws arcs and rounded shapes without antialiasing, which looks
visibly jagged at the sizes this dashboard uses. Everything decorative is
therefore drawn in PIL at 4x and downsampled, then blitted into the canvas as
an image; Tk still draws the text, which it renders well.

All functions return opaque RGB images composited onto ``bg`` so nothing has to
rely on Tk's patchy handling of alpha in PhotoImage.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling factor


def _canvas(width: int, height: int, bg: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (max(1, width * SS), max(1, height * SS)), bg)
    return image, ImageDraw.Draw(image)


def _down(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((max(1, width), max(1, height)), Image.LANCZOS)


def card(
    width: int,
    height: int,
    *,
    bg: str,
    fill: str,
    radius: int = 10,
    border: str | None = None,
    shadow: bool = False,
) -> Image.Image:
    """A rounded panel, optionally with a soft drop shadow."""
    width, height = max(1, width), max(1, height)
    image, draw = _canvas(width, height, bg)
    r = radius * SS

    # Room for the shadow to fall into, but never more than the card can spare:
    # panels are asked to paint at 1px before layout assigns them a width, and
    # a fixed inset would invert the rectangle.
    inset = max(0, min(2 * SS, (width * SS - 1) // 2, (height * SS - 1) // 2))

    box = (inset, inset, width * SS - inset - 1, height * SS - inset - 1)
    if box[2] <= box[0] or box[3] <= box[1]:
        return _down(image, width, height)

    if shadow:
        shade = Image.new("L", image.size, 0)
        ImageDraw.Draw(shade).rounded_rectangle(
            (box[0], box[1] + 2 * SS, box[2], box[3] + 3 * SS), radius=r, fill=52
        )
        shade = shade.filter(ImageFilter.GaussianBlur(3.5 * SS))
        image.paste(Image.new("RGB", image.size, "#0b1220"), mask=shade)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=border, width=SS if border else 0)
    return _down(image, width, height)


def donut(
    diameter: int,
    ratio: float,
    *,
    bg: str,
    fill: str,
    track: str,
    thickness: float = 0.13,
) -> Image.Image:
    """A circular progress ring, filling clockwise from twelve o'clock."""
    diameter = max(8, diameter)
    ratio = max(0.0, min(1.0, float(ratio)))
    image, draw = _canvas(diameter, diameter, bg)

    size = diameter * SS
    pad = int(size * thickness / 2) + SS
    box = (pad, pad, size - pad - 1, size - pad - 1)
    width = max(SS, int(size * thickness))

    draw.arc(box, start=0, end=360, fill=track, width=width)
    if ratio > 0.001:
        draw.arc(box, start=-90, end=-90 + 360 * ratio, fill=fill, width=width)

    return _down(image, diameter, diameter)


def pill(
    width: int,
    height: int,
    ratio: float,
    *,
    bg: str,
    fill: str,
    track: str,
) -> Image.Image:
    """A rounded horizontal progress bar."""
    width, height = max(2, width), max(2, height)
    ratio = max(0.0, min(1.0, float(ratio)))
    image, draw = _canvas(width, height, bg)

    w, h = width * SS, height * SS
    radius = h / 2
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=track)

    filled = int(w * ratio)
    if filled >= h:
        draw.rounded_rectangle((0, 0, filled, h - 1), radius=radius, fill=fill)
    elif filled > 0:
        # Too short to round properly -- draw a circle so the cap stays smooth.
        draw.ellipse((0, 0, h - 1, h - 1), fill=fill)

    return _down(image, width, height)


def bars(
    width: int,
    height: int,
    values: list[float],
    *,
    bg: str,
    fill: str,
    highlight: str | None = None,
    baseline: str | None = None,
    gap_ratio: float = 0.28,
    min_bar: int = 2,
) -> Image.Image:
    """A column chart with rounded tops, scaled to its own maximum."""
    width, height = max(2, width), max(2, height)
    image, draw = _canvas(width, height, bg)
    w, h = width * SS, height * SS

    if baseline:
        draw.rectangle((0, h - SS, w, h), fill=baseline)

    if not values:
        return _down(image, width, height)

    peak = max(values)
    slot = w / len(values)
    bar_w = max(SS, slot * (1 - gap_ratio))
    floor = min_bar * SS
    usable = h - floor - SS

    for index, value in enumerate(values):
        if value <= 0:
            # An empty bucket draws nothing. Giving it the minimum bar height
            # turns a quiet stretch into what looks like a dashed baseline.
            continue
        scaled = 0.0 if peak <= 0 else value / peak
        bar_h = floor + usable * scaled
        x0 = index * slot + (slot - bar_w) / 2
        x1 = x0 + bar_w
        y0 = h - bar_h
        color = highlight if (highlight and index == len(values) - 1) else fill
        radius = min(bar_w / 2, bar_h / 2)
        if radius >= SS:
            draw.rounded_rectangle((x0, y0, x1, h - SS), radius=radius, fill=color)
        else:
            draw.rectangle((x0, y0, x1, h - SS), fill=color)

    return _down(image, width, height)


def dot(size: int, color: str, *, bg: str) -> Image.Image:
    """A small filled circle, used as a legend swatch."""
    size = max(2, size)
    image, draw = _canvas(size, size, bg)
    draw.ellipse((0, 0, size * SS - 1, size * SS - 1), fill=color)
    return _down(image, size, size)


__all__ = ["SS", "bars", "card", "donut", "dot", "pill"]
