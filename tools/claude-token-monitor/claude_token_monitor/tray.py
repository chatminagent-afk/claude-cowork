"""System-tray indicator built on pystray.

The icon lives on its own thread with its own Windows message pump. It never
touches Tk directly -- menu clicks are pushed onto a queue that the Tk thread
drains, because Tk objects may only be used from the thread that created them.
"""

from __future__ import annotations

import queue
from typing import Callable

import pystray

from . import icon as icon_render
from . import startup
from .aggregate import Snapshot, metric_value
from .config import Config
from .formatting import ago, metric_number, money, tokens

# Windows truncates notification-area tooltips; keep well inside the limit.
TOOLTIP_LIMIT = 127


def build_tooltip(snapshot: Snapshot, config: Config) -> str:
    metric = config.gauge_metric
    used = metric_value(snapshot.window_5h, metric)
    ratio = 0.0 if config.limit_5h_tokens <= 0 else used / config.limit_5h_tokens

    lines = [
        f"5h  {ratio * 100:.0f}%  "
        f"{metric_number(used, metric)} / {metric_number(config.limit_5h_tokens, metric)}",
        f"Today  {tokens(snapshot.today.total_tokens)}  {money(snapshot.today.cost_usd)}",
        f"Last call {ago(snapshot.last_activity, snapshot.generated_at)}",
    ]
    text = "\n".join(lines)
    return text[:TOOLTIP_LIMIT]


class TrayIndicator:
    """Owns the pystray icon and forwards menu clicks onto ``commands``."""

    def __init__(self, config: Config, commands: "queue.Queue[tuple]") -> None:
        self.config = config
        self.commands = commands
        self._icon = pystray.Icon(
            "claude-token-monitor",
            icon_render.render_icon(0.0, has_data=False),
            "Claude Code Token Monitor -- starting...",
            menu=self._menu(),
        )
        self._running = False

    # ------------------------------------------------------------------- menu

    def _menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Open dashboard", self._post("show"), default=True),
            pystray.MenuItem("Refresh now", self._post("refresh")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Calibrate limits from history", self._post("calibrate")),
            pystray.MenuItem("Settings...", self._post("settings")),
            pystray.MenuItem(
                "Start at login",
                self._toggle_startup,
                checked=lambda _item: startup.is_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._post("quit")),
        )

    def _post(self, name: str) -> Callable[..., None]:
        def handler(_icon=None, _item=None) -> None:
            self.commands.put((name,))

        return handler

    def _toggle_startup(self, _icon=None, _item=None) -> None:
        startup.toggle()
        self._icon.update_menu()

    # ----------------------------------------------------------------- runtime

    def run(self) -> None:
        """Blocking; call on a dedicated thread."""
        self._running = True
        try:
            self._icon.run()
        finally:
            self._running = False

    def stop(self) -> None:
        try:
            self._icon.stop()
        except Exception:
            pass

    def update(self, snapshot: Snapshot) -> None:
        """Refresh the icon face and tooltip. Safe to call off the Tk thread."""
        used = metric_value(snapshot.window_5h, self.config.gauge_metric)
        limit = max(1, self.config.limit_5h_tokens)
        ratio = used / limit
        has_data = snapshot.all_time.requests > 0

        try:
            self._icon.icon = icon_render.render_icon(
                ratio,
                warn_pct=self.config.warn_pct,
                crit_pct=self.config.crit_pct,
                has_data=has_data,
            )
            self._icon.title = build_tooltip(snapshot, self.config)
        except Exception:
            # A tray update must never take down the polling loop.
            pass

    def notify(self, message: str, title: str = "Claude Code Token Monitor") -> None:
        try:
            self._icon.notify(message, title)
        except Exception:
            pass


__all__ = ["TOOLTIP_LIMIT", "TrayIndicator", "build_tooltip"]
