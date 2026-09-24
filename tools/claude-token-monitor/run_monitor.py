"""Launcher for the tray indicator.

Kept at the repo root so Python puts this directory on ``sys.path``, which lets
the Windows Run key invoke it by absolute path with no PYTHONPATH juggling.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from claude_token_monitor.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
