"""The detail window.

Layout is a hero panel (5-hour ring + 7-day bar), a row of summary cards, a
24-hour activity chart, and tabbed breakdown tables. The decorative chrome is
Pillow-rendered (see ``graphics``) because Tk cannot antialias; Tk draws the
text and owns the tables.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from PIL import ImageTk

from . import graphics
from .aggregate import METRICS, SCOPES, Snapshot, Totals, metric_label, metric_value
from .config import Config
from .formatting import ago, clock, data_size, metric_number, money, tokens, tokens_exact
from .scanner import ScanStats, decode_project_name
from .theme import Fonts, Palette, model_color, resolve_fonts, resolve_palette
from .widgets import ActivityPanel, HeroPanel, StatStrip, stat_items

SCOPE_LABELS = {
    "5h": "Last 5 hours",
    "today": "Today",
    "7d": "Last 7 days",
    "30d": "Last 30 days",
    "all": "All time",
}
_LABEL_TO_SCOPE = {v: k for k, v in SCOPE_LABELS.items()}

METRIC_LABELS = {key: metric_label(key).title() for key in METRICS}
_LABEL_TO_METRIC = {v: k for k, v in METRIC_LABELS.items()}

THEME_LABELS = {"auto": "Match Windows", "light": "Light", "dark": "Dark"}
_LABEL_TO_THEME = {v: k for k, v in THEME_LABELS.items()}

ACTIVITY_HOURS = 24
ACTIVITY_BUCKETS = 48


class Dashboard:
    """Owns the Tk root. Closing the window hides it back to the tray."""

    def __init__(
        self,
        root: tk.Tk,
        config: Config,
        on_refresh: Callable[[], None],
        on_calibrate: Callable[[], None],
        on_config_changed: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self.root = root
        self.config = config
        self.on_refresh = on_refresh
        self.on_calibrate = on_calibrate
        self.on_config_changed = on_config_changed
        self.on_quit = on_quit

        self._snapshot: Snapshot | None = None
        self._stats: ScanStats | None = None
        self._series: list[float] = []
        self._dots: dict[str, ImageTk.PhotoImage] = {}

        root.title("Claude Code Token Monitor")
        root.geometry("1000x720")
        root.minsize(880, 640)
        root.protocol("WM_DELETE_WINDOW", self.hide)

        self.palette = resolve_palette(config.theme)
        self.fonts = resolve_fonts(root)
        self._build()

    # ------------------------------------------------------------------ theme

    def _style(self) -> None:
        pal, fonts = self.palette, self.fonts
        self.root.configure(bg=pal.bg)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=pal.bg)
        style.configure("Surface.TFrame", background=pal.surface)
        style.configure("TLabel", background=pal.bg, foreground=pal.text, font=fonts.body)
        style.configure("Head.TLabel", background=pal.bg, foreground=pal.text, font=fonts.heading)
        style.configure(
            "Muted.TLabel", background=pal.bg, foreground=pal.text_muted, font=fonts.small
        )
        style.configure(
            "Faint.TLabel", background=pal.bg, foreground=pal.text_faint, font=fonts.small
        )

        style.configure(
            "TButton",
            background=pal.surface,
            foreground=pal.text,
            bordercolor=pal.border,
            lightcolor=pal.surface,
            darkcolor=pal.surface,
            focuscolor=pal.surface,
            borderwidth=1,
            relief="flat",
            padding=(12, 6),
            font=fonts.body,
        )
        style.map(
            "TButton",
            background=[("active", pal.surface_alt), ("pressed", pal.surface_alt)],
            bordercolor=[("active", pal.accent)],
        )
        style.configure(
            "Accent.TButton",
            background=pal.accent,
            foreground="#ffffff",
            bordercolor=pal.accent,
            lightcolor=pal.accent,
            darkcolor=pal.accent,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#c8663f"), ("pressed", "#c8663f")],
        )

        style.configure(
            "TCombobox",
            fieldbackground=pal.surface,
            background=pal.surface,
            foreground=pal.text,
            bordercolor=pal.border,
            lightcolor=pal.surface,
            darkcolor=pal.surface,
            arrowcolor=pal.text_muted,
            padding=5,
        )
        # A readonly combobox ignores the base configure() on clam, so the
        # readonly state has to be mapped explicitly or it renders grey.
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", pal.surface), ("disabled", pal.surface)],
            background=[("readonly", pal.surface), ("active", pal.surface_alt)],
            foreground=[("readonly", pal.text)],
            bordercolor=[("focus", pal.accent), ("hover", pal.accent)],
            arrowcolor=[("readonly", pal.text_muted)],
            selectbackground=[("readonly", pal.surface)],
            selectforeground=[("readonly", pal.text)],
        )
        self.root.option_add("*TCombobox*Listbox.background", pal.surface)
        self.root.option_add("*TCombobox*Listbox.foreground", pal.text)
        self.root.option_add("*TCombobox*Listbox.selectBackground", pal.accent)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        # Tabs as a flat segmented control: no borders in any state, so the
        # selected tab reads as continuous with the panel below it.
        style.configure(
            "TNotebook",
            background=pal.bg,
            bordercolor=pal.bg,
            lightcolor=pal.bg,
            darkcolor=pal.bg,
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background=pal.bg,
            foreground=pal.text_muted,
            bordercolor=pal.bg,
            lightcolor=pal.bg,
            darkcolor=pal.bg,
            focuscolor=pal.bg,
            borderwidth=0,
            padding=(18, 9),
            font=fonts.body,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", pal.surface), ("active", pal.surface_alt)],
            foreground=[("selected", pal.text)],
            lightcolor=[("selected", pal.surface)],
            darkcolor=[("selected", pal.surface)],
            bordercolor=[("selected", pal.surface)],
            expand=[("selected", (0, 0, 0, 0))],
        )

        style.configure(
            "Treeview",
            background=pal.surface,
            fieldbackground=pal.surface,
            foreground=pal.text,
            bordercolor=pal.surface,
            lightcolor=pal.surface,
            darkcolor=pal.surface,
            borderwidth=0,
            rowheight=28,
            font=fonts.body,
        )
        style.configure(
            "Treeview.Heading",
            background=pal.surface,
            foreground=pal.text_faint,
            bordercolor=pal.border,
            relief="flat",
            padding=(8, 8),
            font=fonts.tiny_caps,
        )
        style.map(
            "Treeview.Heading",
            background=[("active", pal.surface_alt)],
        )
        style.map(
            "Treeview",
            background=[("selected", pal.selection)],
            foreground=[("selected", pal.text)],
        )

        # Arrow-less scrollbar: clam always draws stepper buttons, so replace
        # the layout with just a trough and a thumb.
        try:
            style.layout(
                "Thin.Vertical.TScrollbar",
                [
                    (
                        "Vertical.Scrollbar.trough",
                        {
                            "sticky": "ns",
                            "children": [
                                (
                                    "Vertical.Scrollbar.thumb",
                                    {"expand": "1", "sticky": "nswe"},
                                )
                            ],
                        },
                    )
                ],
            )
        except tk.TclError:
            pass
        style.configure(
            "Thin.Vertical.TScrollbar",
            background=pal.border,
            troughcolor=pal.surface,
            bordercolor=pal.surface,
            lightcolor=pal.border,
            darkcolor=pal.border,
            borderwidth=0,
            width=8,
        )
        style.map(
            "Thin.Vertical.TScrollbar",
            background=[("active", pal.text_faint)],
        )

        style.configure("TCheckbutton", background=pal.bg, foreground=pal.text, font=fonts.body)
        style.configure("TEntry", fieldbackground=pal.surface, foreground=pal.text, bordercolor=pal.border)

    # ------------------------------------------------------------------ build

    def _build(self) -> None:
        self._style()
        pal, fonts = self.palette, self.fonts

        outer = ttk.Frame(self.root, padding=(18, 14, 18, 0))
        outer.pack(fill="both", expand=True)
        self._outer = outer

        # ---- header -------------------------------------------------------
        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 12))

        titles = ttk.Frame(header)
        titles.pack(side="left")
        ttk.Label(titles, text="Claude Code token usage", style="Head.TLabel").pack(anchor="w")
        self.subtitle = ttk.Label(titles, text="", style="Faint.TLabel")
        self.subtitle.pack(anchor="w", pady=(1, 0))

        ttk.Button(header, text="Refresh", command=self.on_refresh).pack(side="right")
        ttk.Button(header, text="Settings", command=self.open_settings).pack(
            side="right", padx=(0, 8)
        )

        self.scope_var = tk.StringVar(value=SCOPE_LABELS.get(self.config.scope, "Today"))
        scope_box = ttk.Combobox(
            header,
            textvariable=self.scope_var,
            values=[SCOPE_LABELS[s] for s in SCOPES],
            state="readonly",
            width=14,
            font=fonts.body,
        )
        scope_box.pack(side="right", padx=(0, 8))
        scope_box.bind("<<ComboboxSelected>>", self._scope_changed)

        # ---- panels -------------------------------------------------------
        self.hero = HeroPanel(outer, pal, fonts)
        self.hero.pack(fill="x")

        self.stats_strip = StatStrip(outer, pal, fonts)
        self.stats_strip.pack(fill="x", pady=(12, 0))

        self.activity = ActivityPanel(outer, pal, fonts)
        self.activity.pack(fill="x", pady=(12, 0))

        # ---- tables -------------------------------------------------------
        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True, pady=(14, 0))

        self.model_tree = self._make_tree(
            notebook,
            ("gauge", "raw", "cost", "req"),
            ("Model", "Gauge metric", "Raw tokens", "Cost", "Requests"),
            (150, 130, 110, 100),
            dots=True,
        )
        notebook.add(self.model_tree.master, text="By model")

        self.project_tree = self._make_tree(
            notebook,
            ("gauge", "raw", "cost", "req"),
            ("Project", "Gauge metric", "Raw tokens", "Cost", "Requests"),
            (150, 130, 110, 100),
            dots=True,
        )
        notebook.add(self.project_tree.master, text="By project")

        self.mix_tree = self._make_tree(
            notebook,
            ("raw", "share", "weight", "cost"),
            ("Token type", "Tokens", "Share of raw", "Bills at", "Cost"),
            (150, 130, 110, 100),
            dots=False,
        )
        notebook.add(self.mix_tree.master, text="Token mix")

        # ---- status bar ---------------------------------------------------
        status = ttk.Frame(self.root, padding=(18, 10, 18, 12))
        status.pack(fill="x")
        self.status_label = ttk.Label(status, text="Starting...", style="Faint.TLabel")
        self.status_label.pack(side="left")
        ttk.Button(status, text="Hide to tray", command=self.hide).pack(side="right")
        ttk.Button(status, text="Calibrate limits", command=self.on_calibrate).pack(
            side="right", padx=(0, 8)
        )

    def _make_tree(
        self,
        master: tk.Misc,
        columns: tuple[str, ...],
        headings: tuple[str, ...],
        widths: tuple[int, ...],
        dots: bool,
    ) -> ttk.Treeview:
        holder = tk.Frame(master, bg=self.palette.surface, bd=0, highlightthickness=0)
        tree = ttk.Treeview(
            holder,
            columns=columns,
            show="tree headings",
            selectmode="browse",
        )
        tree.heading("#0", text=headings[0], anchor="w")
        tree.column("#0", width=250, minwidth=160, anchor="w", stretch=True)
        for column, heading, width in zip(columns, headings[1:], widths):
            tree.heading(column, text=heading, anchor="e")
            tree.column(column, width=width, anchor="e", stretch=False)

        tree.tag_configure("odd", background=self.palette.surface)
        tree.tag_configure("even", background=self.palette.row_alt)

        scroll = ttk.Scrollbar(
            holder, orient="vertical", command=tree.yview, style="Thin.Vertical.TScrollbar"
        )
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        scroll.pack(side="right", fill="y", pady=6, padx=(0, 4))
        tree.uses_dots = dots  # type: ignore[attr-defined]
        return tree

    def _dot(self, color: str) -> ImageTk.PhotoImage:
        if color not in self._dots:
            self._dots[color] = ImageTk.PhotoImage(
                graphics.dot(9, color, bg=self.palette.surface)
            )
        return self._dots[color]

    # ---------------------------------------------------------------- updates

    def update(self, snapshot: Snapshot, stats: ScanStats | None = None) -> None:
        """Repaint from a snapshot. Never raises into the Tk event loop."""
        try:
            self._update(snapshot, stats)
        except tk.TclError:
            pass

    def set_series(self, series: list[float]) -> None:
        self._series = series

    def _update(self, snapshot: Snapshot, stats: ScanStats | None) -> None:
        self._snapshot = snapshot
        if stats is not None:
            self._stats = stats
        metric = self.config.gauge_metric

        self.subtitle.configure(
            text=f"gauged on {metric_label(metric)}   --   breakdowns scoped to "
            f"{snapshot.scope_label.lower()}"
        )

        self.hero.render(snapshot, self.config, metric)
        self.stats_strip.render(stat_items(snapshot, self.palette))

        peak = max(self._series) if self._series else 0.0
        self.activity.render(
            self._series,
            ACTIVITY_HOURS,
            metric,
            f"peak {metric_number(peak, metric)} per {ACTIVITY_HOURS * 60 // ACTIVITY_BUCKETS}m"
            if peak
            else "",
        )

        self._fill_breakdown(self.model_tree, snapshot.by_model, metric, decode=False)
        self._fill_breakdown(self.project_tree, snapshot.by_project, metric, decode=True)
        self._fill_mix(snapshot.scope_totals)

        parts = [
            f"Updated {clock(snapshot.generated_at)}",
            f"last call {ago(snapshot.last_activity, snapshot.generated_at)}",
        ]
        if self._stats is not None:
            parts.append(
                f"{self._stats.records:,} records / {self._stats.duplicates:,} duplicates "
                f"skipped / {data_size(self._stats.bytes_read)} read in "
                f"{self._stats.elapsed_s:.2f}s"
            )
        self.status_label.configure(text="     ".join(parts))

    def _fill_breakdown(
        self,
        tree: ttk.Treeview,
        data: dict[str, Totals],
        metric: str,
        decode: bool,
    ) -> None:
        tree.delete(*tree.get_children())
        if not data:
            tree.insert("", "end", text="  no usage in scope", values=("", "", "", ""))
            return
        for index, (name, totals) in enumerate(data.items()):
            label = decode_project_name(name) if decode else name
            tree.insert(
                "",
                "end",
                text=f"  {label}",
                image=self._dot(model_color(name)),
                tags=("even" if index % 2 else "odd",),
                values=(
                    metric_number(metric_value(totals, metric), metric),
                    tokens(totals.total_tokens),
                    money(totals.cost_usd),
                    f"{totals.requests:,}",
                ),
            )

    def _fill_mix(self, totals: Totals) -> None:
        self.mix_tree.delete(*self.mix_tree.get_children())
        rows = (
            ("Input", totals.input_tokens, "1.00x", self.palette.accent),
            ("Output", totals.output_tokens, "output rate", "#4f8ff7"),
            ("Cache write (5m)", totals.cache_write_5m_tokens, "1.25x", "#3fb571"),
            ("Cache write (1h)", totals.cache_write_1h_tokens, "2.00x", "#b47ae0"),
            ("Cache read", totals.cache_read_tokens, "0.10x", "#8a94a6"),
        )
        raw = totals.total_tokens or 1
        for index, (label, value, weight, color) in enumerate(rows):
            self.mix_tree.insert(
                "",
                "end",
                text=f"  {label}",
                image=self._dot(color),
                tags=("even" if index % 2 else "odd",),
                values=(tokens_exact(value), f"{value / raw * 100:.1f}%", weight, ""),
            )
        self.mix_tree.insert(
            "",
            "end",
            text="  Total",
            tags=("odd",),
            values=(tokens_exact(totals.total_tokens), "100.0%", "", money(totals.cost_usd)),
        )

    # ----------------------------------------------------------- interactions

    def _scope_changed(self, _event: object = None) -> None:
        scope = _LABEL_TO_SCOPE.get(self.scope_var.get(), "today")
        if scope != self.config.scope:
            self.config.scope = scope
            self.config.validate()
            self._save_config()
            self.on_refresh()

    def _save_config(self) -> None:
        try:
            self.config.save()
        except OSError as exc:
            messagebox.showwarning(
                "Could not save settings",
                f"Settings were not written to disk:\n{exc}",
                parent=self.root,
            )

    def open_settings(self) -> None:
        SettingsDialog(self.root, self.config, self.palette, self.fonts, self._settings_applied)

    def _settings_applied(self, theme_changed: bool) -> None:
        self._save_config()
        self.scope_var.set(SCOPE_LABELS.get(self.config.scope, "Today"))
        if theme_changed:
            self.rebuild()
        self.on_config_changed()
        self.on_refresh()

    def rebuild(self) -> None:
        """Tear down and re-create the UI under a new palette."""
        self.palette = resolve_palette(self.config.theme)
        self._dots.clear()
        for child in self.root.winfo_children():
            child.destroy()
        self._build()
        if self._snapshot is not None:
            self.update(self._snapshot, self._stats)

    def show(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        if self._snapshot is not None:
            self.update(self._snapshot, self._stats)

    def hide(self) -> None:
        self.root.withdraw()


class CalibrationDialog(tk.Toplevel):
    """Two ways to pin the limit Claude Code does not expose on disk."""

    def __init__(
        self,
        parent: tk.Tk,
        palette: Palette,
        fonts: Fonts,
        *,
        metric: str,
        used_now: float,
        suggestions: dict,
        current_limit: int,
        on_apply: Callable[[int, int | None], None],
    ) -> None:
        super().__init__(parent)
        self.palette = palette
        self.metric = metric
        self.used_now = used_now
        self.on_apply = on_apply

        self.title("Calibrate limits")
        self.configure(bg=palette.bg)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=(
                "Claude Code does not record your account's rate limit on disk,\n"
                "so the gauge needs a denominator from somewhere else."
            ),
            style="Muted.TLabel",
            justify="left",
        ).pack(anchor="w")

        ttk.Label(
            frame,
            text=f"Currently set to {metric_number(current_limit, metric, exact=True)}"
            f"   --   {metric_number(used_now, metric, exact=True)} counted right now",
            style="Faint.TLabel",
        ).pack(anchor="w", pady=(6, 16))

        # ---- option A: read it off Claude's own panel ---------------------
        ttk.Label(frame, text="MATCH CLAUDE'S USAGE PANEL", style="Faint.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "The most accurate option. Open Claude > Settings > Usage and\n"
                "type the percentage it shows for the current session."
            ),
            style="Muted.TLabel",
            justify="left",
        ).pack(anchor="w", pady=(2, 8))

        row = ttk.Frame(frame)
        row.pack(fill="x")
        ttk.Label(row, text="Claude shows").pack(side="left")
        self.percent_var = tk.StringVar(value="")
        entry = ttk.Entry(row, textvariable=self.percent_var, width=6)
        entry.pack(side="left", padx=6)
        ttk.Label(row, text="% used").pack(side="left")
        self.sync_button = ttk.Button(
            row, text="Use this", style="Accent.TButton", command=self._apply_percent
        )
        self.sync_button.pack(side="right")

        self.implied_label = ttk.Label(frame, text="", style="Muted.TLabel", justify="left")
        self.implied_label.pack(anchor="w", pady=(8, 0))
        self.percent_var.trace_add("write", lambda *_a: self._preview())
        self._preview()

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=16)

        # ---- option B: infer from local history ---------------------------
        peak_5h, sugg_5h, at_5h = suggestions["5h"]
        peak_7d, sugg_7d, _at7 = suggestions["7d"]
        self._history = (int(sugg_5h), int(sugg_7d))

        ttk.Label(frame, text="INFER FROM YOUR OWN HISTORY", style="Faint.TLabel").pack(anchor="w")
        when = at_5h.astimezone().strftime("%d %b %H:%M") if at_5h else "n/a"
        ttk.Label(
            frame,
            text=(
                f"Peak 5h usage {metric_number(peak_5h, metric, exact=True)} (on {when})\n"
                f"Peak 7d usage {metric_number(peak_7d, metric, exact=True)}\n"
                f"Suggested limits, with headroom:  5h "
                f"{metric_number(sugg_5h, metric, exact=True)}   7d "
                f"{metric_number(sugg_7d, metric, exact=True)}"
            ),
            style="Muted.TLabel",
            justify="left",
        ).pack(anchor="w", pady=(2, 10))

        ttk.Button(frame, text="Use history", command=self._apply_history).pack(anchor="w")

        ttk.Button(frame, text="Cancel", command=self.destroy).pack(anchor="e", pady=(18, 0))
        self.bind("<Escape>", lambda _e: self.destroy())
        entry.focus_set()

    # ------------------------------------------------------------------ logic

    def _parsed_percent(self) -> float | None:
        raw = self.percent_var.get().strip().rstrip("%").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        return value if 0 < value <= 100 else None

    def _preview(self) -> None:
        from .report import limit_from_percent, percent_uncertainty

        percent = self._parsed_percent()
        if percent is None or self.used_now <= 0:
            self.implied_label.configure(
                text="Enter a percentage between 1 and 100." if self.percent_var.get().strip()
                else " "
            )
            self.sync_button.state(["disabled"])
            return

        implied = limit_from_percent(self.used_now, percent)
        low, high = percent_uncertainty(self.used_now, percent)
        self.implied_label.configure(
            text=(
                f"Implied limit  {metric_number(implied, self.metric, exact=True)}\n"
                f"A displayed whole percent is rounded, so the true value sits\n"
                f"between {metric_number(low, self.metric, exact=True)} and "
                f"{metric_number(high, self.metric, exact=True)}."
            )
        )
        self.sync_button.state(["!disabled"])

    def _apply_percent(self) -> None:
        from .report import limit_from_percent

        percent = self._parsed_percent()
        if percent is None or self.used_now <= 0:
            return
        self.destroy()
        # Only the 5h window can be derived this way; leave 7d untouched.
        self.on_apply(int(limit_from_percent(self.used_now, percent)), None)

    def _apply_history(self) -> None:
        self.destroy()
        self.on_apply(self._history[0], self._history[1])


class SettingsDialog(tk.Toplevel):
    """Modal editor for the tunable settings."""

    def __init__(
        self,
        parent: tk.Tk,
        config: Config,
        palette: Palette,
        fonts: Fonts,
        on_apply: Callable[[bool], None],
    ) -> None:
        super().__init__(parent)
        self.config_obj = config
        self.palette = palette
        self.on_apply = on_apply
        self._theme_before = config.theme

        self.title("Settings")
        self.configure(bg=palette.bg)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        self.vars: dict[str, tk.Variable] = {}
        row = 0

        ttk.Label(frame, text="LIMITS", style="Faint.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        row += 1
        row = self._entry(frame, row, "limit_5h_tokens", "5-hour limit", str(config.limit_5h_tokens))
        row = self._entry(frame, row, "limit_7d_tokens", "7-day limit", str(config.limit_7d_tokens))
        row = self._combo(
            frame, row, "gauge_metric", "Gauge metric",
            METRIC_LABELS.get(config.gauge_metric, ""), list(METRIC_LABELS.values()),
        )

        ttk.Label(frame, text="APPEARANCE", style="Faint.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(14, 6)
        )
        row += 1
        row = self._combo(
            frame, row, "theme", "Theme",
            THEME_LABELS.get(config.theme, "Match Windows"), list(THEME_LABELS.values()),
        )
        row = self._entry(frame, row, "warn_pct", "Amber at (0-1)", str(config.warn_pct))
        row = self._entry(frame, row, "crit_pct", "Red at (0-1)", str(config.crit_pct))

        ttk.Label(frame, text="COLLECTION", style="Faint.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(14, 6)
        )
        row += 1
        row = self._entry(
            frame, row, "poll_interval_s", "Refresh every (seconds)", str(config.poll_interval_s)
        )
        row = self._entry(
            frame, row, "retention_days", "Keep history (days)", str(config.retention_days)
        )

        sidechain_var = tk.BooleanVar(value=config.include_sidechains)
        ttk.Checkbutton(
            frame, text="Include subagent (sidechain) usage", variable=sidechain_var
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(8, 2))
        self.vars["include_sidechains"] = sidechain_var
        row += 1

        from . import startup

        self.startup_var = tk.BooleanVar(value=startup.is_enabled())
        ttk.Checkbutton(
            frame, text="Start automatically when I sign in", variable=self.startup_var
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
        row += 1

        ttk.Label(
            frame,
            text=(
                "Claude Code does not publish your rate limit. Use\n"
                "'Calibrate limits' to derive it from your own peak usage."
            ),
            style="Muted.TLabel",
            justify="left",
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(14, 4))
        row += 1

        buttons = ttk.Frame(frame)
        buttons.grid(row=row, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Save", style="Accent.TButton", command=self._save).pack(
            side="right", padx=(0, 8)
        )

        frame.columnconfigure(1, weight=1, minsize=200)
        self.bind("<Escape>", lambda _e: self.destroy())

    def _entry(self, frame, row: int, key: str, label: str, value: str) -> int:
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 14))
        var = tk.StringVar(value=value)
        ttk.Entry(frame, textvariable=var, width=26).grid(row=row, column=1, sticky="ew", pady=5)
        self.vars[key] = var
        return row + 1

    def _combo(self, frame, row: int, key: str, label: str, value: str, values: list[str]) -> int:
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 14))
        var = tk.StringVar(value=value)
        ttk.Combobox(
            frame, textvariable=var, values=values, state="readonly", width=24
        ).grid(row=row, column=1, sticky="ew", pady=5)
        self.vars[key] = var
        return row + 1

    def _save(self) -> None:
        config = self.config_obj
        try:
            config.limit_5h_tokens = int(float(self.vars["limit_5h_tokens"].get()))
            config.limit_7d_tokens = int(float(self.vars["limit_7d_tokens"].get()))
            config.poll_interval_s = float(self.vars["poll_interval_s"].get())
            config.warn_pct = float(self.vars["warn_pct"].get())
            config.crit_pct = float(self.vars["crit_pct"].get())
            config.retention_days = int(float(self.vars["retention_days"].get()))
        except (TypeError, ValueError):
            messagebox.showerror(
                "Invalid value",
                "Limits, interval, thresholds and retention must be numbers.",
                parent=self,
            )
            return

        config.gauge_metric = _LABEL_TO_METRIC.get(
            str(self.vars["gauge_metric"].get()), config.gauge_metric
        )
        config.theme = _LABEL_TO_THEME.get(str(self.vars["theme"].get()), config.theme)
        config.include_sidechains = bool(self.vars["include_sidechains"].get())
        config.validate()

        from . import startup

        if self.startup_var.get() != startup.is_enabled():
            ok = startup.enable() if self.startup_var.get() else startup.disable()
            if not ok:
                messagebox.showwarning(
                    "Startup setting",
                    "Could not update the run-at-login registry entry.",
                    parent=self,
                )

        theme_changed = config.theme != self._theme_before
        self.destroy()
        self.on_apply(theme_changed)


__all__ = [
    "ACTIVITY_BUCKETS",
    "ACTIVITY_HOURS",
    "CalibrationDialog",
    "Dashboard",
    "SettingsDialog",
]
