"""Manual GUI smoke test -- requires a desktop session.

Not picked up by ``unittest discover`` (the filename is deliberately not
``test_*``). Builds the real dashboard against real transcript data in both
palettes, forces a render, and writes screenshots so the result can be
inspected rather than assumed.

    python tests/smoke_gui.py [output_dir]
"""

from __future__ import annotations

import sys
import time
import tkinter as tk
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageGrab  # noqa: E402

from claude_token_monitor import graphics  # noqa: E402
from claude_token_monitor.config import Config  # noqa: E402
from claude_token_monitor.dashboard import (  # noqa: E402
    ACTIVITY_BUCKETS,
    ACTIVITY_HOURS,
    Dashboard,
)
from claude_token_monitor.icon import render_icon  # noqa: E402
from claude_token_monitor.report import collect  # noqa: E402
from claude_token_monitor.theme import DARK, LIGHT  # noqa: E402


def icon_strip(out_dir: Path) -> Path:
    """Render the tray icon across its whole state range, side by side."""
    ratios = [0.05, 0.25, 0.55, 0.62, 0.8, 0.9, 1.0]
    tiles = [render_icon(r) for r in ratios]
    tiles.append(render_icon(0.0, has_data=False))

    pad = 10
    size = tiles[0].width
    strip = Image.new(
        "RGBA",
        (len(tiles) * (size + pad) + pad + size + pad, size + 2 * pad),
        (244, 245, 247, 255),
    )
    for index, tile in enumerate(tiles):
        strip.paste(tile, (pad + index * (size + pad), pad), tile)

    # True notification-area scale, magnified, to confirm legibility at 16px.
    small = render_icon(0.62).resize((16, 16), Image.LANCZOS)
    strip.paste(
        small.resize((size, size), Image.NEAREST),
        (pad + len(tiles) * (size + pad), pad),
        small.resize((size, size), Image.NEAREST),
    )

    path = out_dir / "tray-icons.png"
    strip.save(path)
    return path


def graphics_sheet(out_dir: Path) -> Path:
    """Every rendered primitive at several states, on both palettes."""
    rows = []
    for palette in (LIGHT, DARK):
        width, height = 720, 150
        sheet = Image.new("RGB", (width, height), palette.bg)

        for index, ratio in enumerate((0.08, 0.35, 0.62, 0.88, 1.0)):
            color = (
                palette.crit if ratio >= 0.85 else palette.warn if ratio >= 0.6 else palette.ok
            )
            sheet.paste(
                graphics.donut(
                    92, ratio, bg=palette.bg, fill=color, track=palette.track
                ),
                (16 + index * 104, 12),
            )
            sheet.paste(
                graphics.pill(
                    92, 10, ratio, bg=palette.bg, fill=color, track=palette.track
                ),
                (16 + index * 104, 116),
            )

        series = [
            (i % 7) ** 2 + (i % 3) * 4 + (12 if i > 34 else 0) for i in range(ACTIVITY_BUCKETS)
        ]
        sheet.paste(
            graphics.bars(
                150,
                92,
                series,
                bg=palette.bg,
                fill=palette.accent,
                baseline=palette.border,
            ),
            (548, 12),
        )
        rows.append(sheet)

    combined = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)))
    y = 0
    for row in rows:
        combined.paste(row, (0, y))
        y += row.height

    path = out_dir / "graphics.png"
    combined.save(path)
    return path


def capture(window: tk.Misc, path: Path) -> None:
    window.update_idletasks()
    for _ in range(6):
        window.update()
        time.sleep(0.12)
    x, y = window.winfo_rootx(), window.winfo_rooty()
    box = (x, y, x + window.winfo_width(), y + window.winfo_height())
    ImageGrab.grab(bbox=box, all_screens=True).save(path)


def shoot_dashboard(theme: str, out_dir: Path, snapshot, stats, series) -> Path:
    config = Config.load()
    config.theme = theme
    config.validate()

    root = tk.Tk()
    dashboard = Dashboard(
        root,
        config,
        on_refresh=lambda: None,
        on_calibrate=lambda: None,
        on_config_changed=lambda: None,
        on_quit=root.quit,
    )
    dashboard.set_series(series)
    dashboard.update(snapshot, stats)

    root.geometry("1000x780+40+30")
    root.deiconify()
    root.attributes("-topmost", True)
    root.lift()
    root.update_idletasks()
    root.update()
    # Panels size themselves from their <Configure> event, so paint twice.
    dashboard.update(snapshot, stats)

    path = out_dir / f"dashboard-{theme}.png"
    capture(root, path)
    root.destroy()
    return path


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)

    config = Config.load()
    aggregator, _scanner, stats = collect(config)
    now = datetime.now(timezone.utc)
    snapshot = aggregator.snapshot(now=now, scope=config.scope)
    series = aggregator.timeline(
        now=now,
        span=timedelta(hours=ACTIVITY_HOURS),
        buckets=ACTIVITY_BUCKETS,
        metric=config.gauge_metric,
    )
    print(f"loaded {len(aggregator)} records in {stats.elapsed_s:.2f}s")
    print(f"activity buckets non-zero: {sum(1 for v in series if v)}/{len(series)}")

    for theme in ("light", "dark"):
        print(f"dashboard ({theme:5}) -> {shoot_dashboard(theme, out_dir, snapshot, stats, series)}")

    print(f"tray icon strip      -> {icon_strip(out_dir)}")
    print(f"graphics sheet       -> {graphics_sheet(out_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
