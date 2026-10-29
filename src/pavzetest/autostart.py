"""Samodejni zagon ob prijavi v Windows (`HKCU\\...\\CurrentVersion\\Run`). Register je vbrizgljiv — testi tečejo
brez pravega registra."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

from pavzetest.identity import APP_NAME

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_PACKAGE = __name__.partition(".")[0]


class Registry(Protocol):
    def get(self, name: str) -> str | None: ...
    def set(self, name: str, value: str) -> None: ...
    def delete(self, name: str) -> None: ...


class WindowsRegistry:
    """Pravi register trenutnega uporabnika (brez skrbniških pravic)."""

    def get(self, name: str) -> str | None:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
                return winreg.QueryValueEx(key, name)[0]
        except OSError:
            return None

    def set(self, name: str, value: str) -> None:
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    def delete(self, name: str) -> None:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass


def launch_command() -> str:
    """Ukaz zagona: zapakirana aplikacija = njen .exe; iz kode = `pythonw -m <paket>` (brez konzole)."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")
    return f'"{pythonw if pythonw.is_file() else exe}" -m {_PACKAGE}'


def enable(command: str | None = None, *, registry: Registry | None = None) -> None:
    (registry or WindowsRegistry()).set(APP_NAME, command or launch_command())


def disable(*, registry: Registry | None = None) -> None:
    (registry or WindowsRegistry()).delete(APP_NAME)


def is_enabled(*, registry: Registry | None = None) -> bool:
    return (registry or WindowsRegistry()).get(APP_NAME) is not None
