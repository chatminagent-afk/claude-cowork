"""Command-line entry point.

    python -m claude_token_monitor              # tray indicator
    python -m claude_token_monitor --report     # one-shot text report
    python -m claude_token_monitor --calibrate  # suggest limits from history
    python -m claude_token_monitor --window     # dashboard only, no tray
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .aggregate import SCOPES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claude_token_monitor",
        description="Real-time Claude Code token usage indicator.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="print a one-shot usage report and exit",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="suggest rate-limit values from your own usage history",
    )
    parser.add_argument(
        "--sync-limit",
        type=float,
        metavar="PCT",
        help=(
            "set the 5h limit from the percentage Claude's own usage panel "
            "shows right now (Settings > Usage), e.g. --sync-limit 88"
        ),
    )
    parser.add_argument(
        "--used",
        type=float,
        metavar="N",
        help=(
            "with --sync-limit, the usage figure to pair the percentage with "
            "(defaults to the current count; supply this to pair with an "
            "earlier reading such as a screenshot)"
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="with --calibrate or --sync-limit, save the derived limits",
    )
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        help="breakdown scope for --report",
    )
    parser.add_argument(
        "--window",
        action="store_true",
        help="run the dashboard without a tray icon",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.sync_limit is not None:
        from .config import Config
        from .report import sync_limit

        try:
            print(
                sync_limit(
                    Config.load(), args.sync_limit, apply=args.apply, used=args.used
                )
            )
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.calibrate:
        from .config import Config
        from .report import calibrate

        print(calibrate(Config.load(), apply=args.apply))
        return 0

    if args.report:
        from .report import main as report_main

        return report_main(scope=args.scope)

    from .app import main as app_main

    return app_main(use_tray=not args.window)


if __name__ == "__main__":
    sys.exit(main())
