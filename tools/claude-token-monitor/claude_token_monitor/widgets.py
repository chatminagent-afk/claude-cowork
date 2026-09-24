"""Composite canvas panels for the dashboard.

Each panel paints a Pillow-rendered background (rounded card, ring, bar, chart)
and then draws crisp Tk text on top. Panels re-render on ``<Configure>`` so they
stay correct through window resizes, and they keep their own PhotoImage
references alive -- Tk drops images that nothing holds.
"""

from __future__ import annotations

import tkinter as tk

from PIL import ImageTk

from . import graphics
from .formatting import duration, metric_number, money, tokens
from .theme import Fonts, Palette


class Panel(tk.Canvas):
    """Base canvas with theme access and image lifetime management."""

    def __init__(self, master: tk.Misc, palette: Palette, fonts: Fonts, height: int) -> None:
        super().__init__(
            master,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=palette.bg,
        )
        self.palette = palette
        self.fonts = fonts
        self._photos: list[ImageTk.PhotoImage] = []
        self._payload: tuple | None = None
        self.bind("<Configure>", self._on_configure)

    # -------------------------------------------------------------- plumbing

    def _on_configure(self, _event: object = None) -> None:
        if self._payload is not None:
            self._repaint()

    def render(self, *payload) -> None:
        self._payload = payload
        self._repaint()

    def _repaint(self) -> None:
        self.delete("all")
        self._photos.clear()
        if self._payload is None:
            return
        width = self.winfo_width()
        if width <= 1:
            return
        try:
            self._paint(width, self.winfo_height(), *self._payload)
        except tk.TclError:
            pass

    def _paint(self, width: int, height: int, *payload) -> None:  # pragma: no cover
        raise NotImplementedError

    def _blit(self, image, x: int, y: int) -> None:
        photo = ImageTk.PhotoImage(image)
        self._photos.append(photo)
        self.create_image(x, y, image=photo, anchor="nw")

    def _card(self, x: int, y: int, w: int, h: int, radius: int = 12) -> None:
        self._blit(
            graphics.card(
                w,
                h,
                bg=self.palette.bg,
                fill=self.palette.surface,
                radius=radius,
                border=None if self.palette.shadow else self.palette.border,
                shadow=self.palette.shadow,
            ),
            x,
            y,
        )

    def _label(self, x, y, text, font, color, anchor="nw") -> int:
        return self.create_text(x, y, text=text, font=font, fill=color, anchor=anchor)

    def status_color(self, ratio: float, warn: float, crit: float, live: bool = True) -> str:
        if not live:
            return self.palette.idle
        if ratio >= crit:
            return self.palette.crit
        if ratio >= warn:
            return self.palette.warn
        return self.palette.ok


class HeroPanel(Panel):
    """The 5-hour ring plus the 7-day bar."""

    HEIGHT = 176

    def __init__(self, master, palette, fonts) -> None:
        super().__init__(master, palette, fonts, self.HEIGHT)

    def _paint(self, width, height, snapshot, config, metric) -> None:
        from .aggregate import metric_value

        pal, fonts = self.palette, self.fonts
        self._card(0, 0, width, height)

        live = snapshot.all_time.requests > 0

        # ---- 5-hour ring -------------------------------------------------
        used = metric_value(snapshot.window_5h, metric)
        limit = max(1, config.limit_5h_tokens)
        ratio = used / limit
        color = self.status_color(ratio, config.warn_pct, config.crit_pct, live)

        ring = 108
        ring_x, ring_y = 26, (height - ring) // 2 - 8
        self._blit(
            graphics.donut(
                ring,
                min(1.0, ratio),
                bg=pal.surface,
                fill=color,
                track=pal.track,
            ),
            ring_x,
            ring_y,
        )
        self._label(
            ring_x + ring // 2,
            ring_y + ring // 2 - 6,
            f"{min(ratio, 9.99) * 100:.0f}%",
            fonts.donut,
            pal.text,
            anchor="center",
        )
        self._label(
            ring_x + ring // 2,
            ring_y + ring // 2 + 16,
            "of 5h limit",
            fonts.small,
            pal.text_faint,
            anchor="center",
        )

        # ---- 5-hour detail ----------------------------------------------
        left = ring_x + ring + 30
        self._label(left, 26, "5-HOUR ROLLING WINDOW", fonts.tiny_caps, pal.text_faint)
        self._label(
            left,
            44,
            f"{metric_number(used, metric, exact=True)}"
            f"  /  {metric_number(limit, metric, exact=True)}",
            fonts.metric_lg,
            pal.text,
        )

        bits = [
            f"{money(snapshot.window_5h.cost_usd)}",
            f"{snapshot.window_5h.requests} requests",
            f"raw {tokens(snapshot.window_5h.total_tokens)}",
        ]
        resets = snapshot.window_5h_resets_in
        if resets is not None:
            bits.append(f"frees up in {duration(resets)}")
        self._label(left, 74, "   ".join(bits), fonts.small, pal.text_muted)

        # ---- 7-day bar ---------------------------------------------------
        used_7d = metric_value(snapshot.window_7d, metric)
        limit_7d = max(1, config.limit_7d_tokens)
        ratio_7d = used_7d / limit_7d
        color_7d = self.status_color(ratio_7d, config.warn_pct, config.crit_pct, live)

        bar_y = height - 46
        self._label(left, bar_y - 18, "7-DAY ROLLING WINDOW", fonts.tiny_caps, pal.text_faint)

        right_text = (
            f"{metric_number(used_7d, metric)} / {metric_number(limit_7d, metric)}"
            f"   {min(ratio_7d, 9.99) * 100:.0f}%"
        )
        text_id = self._label(
            width - 26, bar_y + 5, right_text, fonts.small_bold, pal.text, anchor="e"
        )
        bounds = self.bbox(text_id)
        bar_right = (bounds[0] - 16) if bounds else (width - 120)
        bar_w = max(40, bar_right - left)

        self._blit(
            graphics.pill(
                bar_w,
                10,
                min(1.0, ratio_7d),
                bg=pal.surface,
                fill=color_7d,
                track=pal.track,
            ),
            left,
            bar_y,
        )


class StatStrip(Panel):
    """A row of small metric cards."""

    HEIGHT = 92

    def __init__(self, master, palette, fonts) -> None:
        super().__init__(master, palette, fonts, self.HEIGHT)

    def _paint(self, width, height, items) -> None:
        pal, fonts = self.palette, self.fonts
        if not items:
            return

        gap = 12
        count = len(items)
        card_w = (width - gap * (count - 1)) / count

        for index, (label, value, sub, accent) in enumerate(items):
            x = int(index * (card_w + gap))
            w = int(card_w)
            self._card(x, 0, w, height, radius=10)

            self._label(x + 16, 16, label.upper(), fonts.tiny_caps, pal.text_faint)
            self._label(x + 16, 34, value, fonts.metric, pal.text)
            self._label(x + 16, 60, sub, fonts.small, pal.text_muted)

            if accent:
                self._blit(
                    graphics.card(
                        3, height - 32, bg=pal.surface, fill=accent, radius=2
                    ),
                    x + 6,
                    16,
                )


class ActivityPanel(Panel):
    """Recent usage as a column chart."""

    HEIGHT = 116

    def __init__(self, master, palette, fonts) -> None:
        super().__init__(master, palette, fonts, self.HEIGHT)

    def _paint(self, width, height, series, span_hours, metric, peak_label) -> None:
        pal, fonts = self.palette, self.fonts
        self._card(0, 0, width, height)

        self._label(20, 16, f"ACTIVITY  --  LAST {span_hours}H", fonts.tiny_caps, pal.text_faint)
        self._label(width - 20, 16, peak_label, fonts.small, pal.text_muted, anchor="ne")

        chart_x, chart_y = 20, 40
        chart_w = max(20, width - 40)
        chart_h = max(10, height - chart_y - 26)

        if not any(series):
            self._label(
                width // 2,
                chart_y + chart_h // 2,
                "no usage in this window",
                fonts.small,
                pal.text_faint,
                anchor="center",
            )
        else:
            self._blit(
                graphics.bars(
                    chart_w,
                    chart_h,
                    series,
                    bg=pal.surface,
                    fill=pal.accent,
                    highlight=pal.accent,
                    baseline=pal.border,
                ),
                chart_x,
                chart_y,
            )

        axis_y = chart_y + chart_h + 6
        self._label(chart_x, axis_y, f"-{span_hours}h", fonts.small, pal.text_faint)
        self._label(
            chart_x + chart_w // 2, axis_y, f"-{span_hours // 2}h", fonts.small,
            pal.text_faint, anchor="n",
        )
        self._label(chart_x + chart_w, axis_y, "now", fonts.small, pal.text_faint, anchor="ne")


def stat_items(snapshot, palette: Palette) -> list[tuple[str, str, str, str]]:
    """The four summary cards, in display order."""
    return [
        (
            "Today",
            tokens(snapshot.today.total_tokens),
            f"{money(snapshot.today.cost_usd)}   {snapshot.today.requests} req",
            palette.accent,
        ),
        (
            "Current session",
            tokens(snapshot.active_session.total_tokens),
            f"{money(snapshot.active_session.cost_usd)}   "
            f"{snapshot.active_session.requests} req",
            palette.ok,
        ),
        (
            "Last 7 days",
            tokens(snapshot.window_7d.total_tokens),
            f"{money(snapshot.window_7d.cost_usd)}   {snapshot.window_7d.requests} req",
            palette.text_faint,
        ),
        (
            "All retained",
            tokens(snapshot.all_time.total_tokens),
            f"{money(snapshot.all_time.cost_usd)}   {snapshot.all_time.requests} req",
            palette.text_faint,
        ),
    ]


__all__ = ["ActivityPanel", "HeroPanel", "Panel", "StatStrip", "stat_items"]
