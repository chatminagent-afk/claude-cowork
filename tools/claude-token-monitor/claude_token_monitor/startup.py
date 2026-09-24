"""Run-at-login registration via the per-user Run key.

The registry approach avoids creating shell shortcuts through COM, needs no
elevation, and is trivially reversible.
"""

from __future__ import annotations

import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "ClaudeTokenMonitor"


def _winreg():
    """Import winreg lazily so the module stays importable off Windows."""
    try:
        import winreg
    except ImportError:  # pragma: no cover - non-Windows
        return None
    return winreg


def launcher_script() -> Path:
    """The repo-root script Windows should launch."""
    return Path(__file__).resolve().parent.parent / "run_monitor.py"


def pythonw_executable() -> Path:
    """``pythonw.exe`` if available, so no console window flashes at login."""
    current = Path(sys.executable)
    candidate = current.with_name("pythonw.exe")
    return candidate if candidate.exists() else current


def startup_command() -> str:
    return f'"{pythonw_executable()}" "{launcher_script()}"'


def is_enabled() -> bool:
    winreg = _winreg()
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _kind = winreg.QueryValueEx(key, VALUE_NAME)
    except (OSError, FileNotFoundError):
        return False
    return bool(value)


def enable() -> bool:
    winreg = _winreg()
    if winreg is None:
        return False
    try:
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, startup_command())
    except OSError:
        return False
    return True


def disable() -> bool:
    winreg = _winreg()
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, VALUE_NAME)
    except (OSError, FileNotFoundError):
        return False
    return True


def toggle() -> bool:
    """Flip the setting; returns the resulting enabled state."""
    if is_enabled():
        disable()
        return False
    enable()
    return is_enabled()


__all__ = [
    "RUN_KEY",
    "VALUE_NAME",
    "disable",
    "enable",
    "is_enabled",
    "launcher_script",
    "pythonw_executable",
    "startup_command",
    "toggle",
]
