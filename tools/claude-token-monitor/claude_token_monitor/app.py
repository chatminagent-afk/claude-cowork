"""Application coordinator.

Three threads, with a strict rule about who may touch what:

* **Tk thread** (the main thread) owns every widget. Nothing else calls into Tk.
* **Poller thread** owns the scanner, reads the filesystem, and feeds the
  aggregator. It hands finished snapshots to the Tk thread through a queue.
* **Tray thread** owns the pystray message pump. Menu clicks go onto the same
  queue rather than being executed inline.

The aggregator is the only object shared for read/write, and it takes its own
lock internally.
"""

from __future__ import annotations

import logging
import queue
import sys
import threading
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import messagebox

from .aggregate import FIVE_HOURS, Aggregator, Snapshot, metric_value
from .config import Config, config_dir, config_path
from .dashboard import (
    ACTIVITY_BUCKETS,
    ACTIVITY_HOURS,
    CalibrationDialog,
    Dashboard,
)
from .report import build_scanner, suggest_limits
from .scanner import ScanStats

log = logging.getLogger("claude_token_monitor")


def _setup_logging() -> None:
    directory = config_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = logging.FileHandler(
            directory / "monitor.log", encoding="utf-8"
        )
    except OSError:
        handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    )
    log.addHandler(handler)
    log.setLevel(logging.INFO)


class MonitorApp:
    def __init__(self, config: Config | None = None, use_tray: bool = True) -> None:
        self.first_run = not config_path().exists()
        self.config = config or Config.load()
        self.config.validate()
        self.use_tray = use_tray

        self.scanner = build_scanner(self.config)
        self.aggregator = Aggregator(retention_days=self.config.retention_days)

        self.commands: "queue.Queue[tuple]" = queue.Queue()
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._rebuild = threading.Event()
        self._calibrated = not self.first_run
        self._last_stats: ScanStats | None = None

        self.root = tk.Tk()
        self.root.withdraw()
        self.dashboard = Dashboard(
            self.root,
            self.config,
            on_refresh=self.request_refresh,
            on_calibrate=self.calibrate_interactive,
            on_config_changed=self.config_changed,
            on_quit=self.shutdown,
        )
        self._set_window_icon()

        self.tray = None
        if use_tray:
            try:
                from .tray import TrayIndicator

                self.tray = TrayIndicator(self.config, self.commands)
            except Exception:
                log.exception("tray unavailable; continuing without it")
                self.tray = None

    # ------------------------------------------------------------------ setup

    def _set_window_icon(self) -> None:
        try:
            from PIL import ImageTk

            from .icon import render_icon

            self._icon_image = ImageTk.PhotoImage(render_icon(0.0, has_data=False))
            self.root.iconphoto(True, self._icon_image)
        except Exception:
            log.debug("window icon unavailable", exc_info=True)

    # ---------------------------------------------------------------- lifecycle

    def run(self) -> int:
        poller = threading.Thread(target=self._poll_loop, name="poller", daemon=True)
        poller.start()

        if self.tray is not None:
            threading.Thread(target=self.tray.run, name="tray", daemon=True).start()
        else:
            # Without a tray there is no other way back to the window.
            self.root.after(200, self.dashboard.show)

        self.root.after(120, self._pump)
        try:
            self.root.mainloop()
        finally:
            self._stop.set()
            self._wake.set()
            if self.tray is not None:
                self.tray.stop()
        return 0

    def shutdown(self) -> None:
        self._stop.set()
        self._wake.set()
        if self.tray is not None:
            self.tray.stop()
        try:
            self.root.quit()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ poller

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._poll_once()
            except Exception:
                log.exception("poll failed")
            self._wake.wait(self.config.poll_interval_s)
            self._wake.clear()

    def _poll_once(self) -> None:
        if self._rebuild.is_set():
            self._rebuild.clear()
            self.scanner = build_scanner(self.config)
            self.aggregator.retention_days = self.config.retention_days
            self.aggregator.clear()

        records = self.scanner.poll()
        stats = self.scanner.last_stats
        self.aggregator.add(records)

        if not self._calibrated and len(self.aggregator):
            self._auto_calibrate()

        now = datetime.now(timezone.utc)
        snapshot = self.aggregator.snapshot(now=now, scope=self.config.scope)
        series = self.aggregator.timeline(
            now=now,
            span=timedelta(hours=ACTIVITY_HOURS),
            buckets=ACTIVITY_BUCKETS,
            metric=self.config.gauge_metric,
        )
        if self.tray is not None:
            self.tray.update(snapshot)
        self.commands.put(("snapshot", snapshot, stats, series))

    def _auto_calibrate(self) -> None:
        """On first launch, derive limits instead of showing an invented number."""
        self._calibrated = True
        try:
            suggestions = suggest_limits(self.aggregator, self.config.gauge_metric)
            self.config.limit_5h_tokens = max(1, int(suggestions["5h"][1]))
            self.config.limit_7d_tokens = max(1, int(suggestions["7d"][1]))
            self.config.validate()
            self.config.save()
            log.info(
                "auto-calibrated limits: 5h=%s 7d=%s",
                self.config.limit_5h_tokens,
                self.config.limit_7d_tokens,
            )
            self.commands.put(
                (
                    "notify",
                    "Limits calibrated from your usage history. "
                    "Adjust them any time in Settings.",
                )
            )
        except Exception:
            log.exception("auto-calibration failed")

    # -------------------------------------------------------------- Tk pumping

    def _pump(self) -> None:
        try:
            while True:
                self._handle(self.commands.get_nowait())
        except queue.Empty:
            pass
        except Exception:
            log.exception("command handling failed")
        if not self._stop.is_set():
            try:
                self.root.after(120, self._pump)
            except tk.TclError:
                pass

    def _handle(self, command: tuple) -> None:
        name = command[0]
        if name == "snapshot":
            snapshot: Snapshot = command[1]
            self._last_stats = command[2]
            self.dashboard.set_series(command[3])
            self.dashboard.update(snapshot, self._last_stats)
        elif name == "show":
            self.dashboard.show()
        elif name == "refresh":
            self.request_refresh()
        elif name == "settings":
            self.dashboard.show()
            self.dashboard.open_settings()
        elif name == "calibrate":
            self.dashboard.show()
            self.calibrate_interactive()
        elif name == "notify":
            if self.tray is not None:
                self.tray.notify(str(command[1]))
        elif name == "quit":
            self.shutdown()

    # ------------------------------------------------------------------ actions

    def request_refresh(self) -> None:
        self._wake.set()

    def config_changed(self) -> None:
        """Re-read settings that affect how data is collected."""
        self.aggregator.retention_days = self.config.retention_days
        if self.scanner.include_sidechains != self.config.include_sidechains:
            self._rebuild.set()
        self.request_refresh()

    def calibrate_interactive(self) -> None:
        if not len(self.aggregator):
            messagebox.showinfo(
                "Calibrate limits",
                "No usage history has been loaded yet. Try again in a moment.",
                parent=self.root,
            )
            return

        metric = self.config.gauge_metric
        used_now = metric_value(
            self.aggregator.totals(datetime.now(timezone.utc) - FIVE_HOURS), metric
        )
        CalibrationDialog(
            self.root,
            self.dashboard.palette,
            self.dashboard.fonts,
            metric=metric,
            used_now=used_now,
            suggestions=suggest_limits(self.aggregator, metric),
            current_limit=self.config.limit_5h_tokens,
            on_apply=self._apply_limits,
        )

    def _apply_limits(self, limit_5h: int, limit_7d: int | None) -> None:
        self.config.limit_5h_tokens = max(1, int(limit_5h))
        if limit_7d is not None:
            self.config.limit_7d_tokens = max(1, int(limit_7d))
        self.config.validate()
        try:
            self.config.save()
        except OSError as exc:
            messagebox.showwarning("Could not save settings", str(exc), parent=self.root)
        log.info(
            "limits set: 5h=%s 7d=%s",
            self.config.limit_5h_tokens,
            self.config.limit_7d_tokens,
        )
        self.request_refresh()


def main(use_tray: bool = True) -> int:
    _setup_logging()
    try:
        return MonitorApp(use_tray=use_tray).run()
    except Exception:
        log.exception("fatal error")
        raise


__all__ = ["MonitorApp", "main"]
