"""Okno aplikacije v Windows: prosojnost celega okna (plastno okno, `SetLayeredWindowAttributes`).

pywebview `transparent=True` na Windows namizja ne pokaže (preizkus Studia 2026-10-29: okno ostane enakomerne
barve) — prosojno ozadje se zato naredi s prosojnostjo okna. Prosojno je tudi besedilo: krepka pisava, dober kontrast.
Okno NiceGUI teče v podprocesu, zato ga poiščemo po naslovu (`ui.run(title=APP_NAME)`)."""
from __future__ import annotations

import sys
from typing import Any

from pavzetest.identity import APP_NAME

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x2
MIN_PERCENT = 10                 # povsem prosojno okno bi se „izgubilo"


def _user32() -> Any:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.FindWindowW.restype = wintypes.HWND
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
    user32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD]
    return user32


def set_opacity(percent: int, *, title: str = APP_NAME, user32: Any | None = None) -> bool:
    """Prosojnost okna `title` v odstotkih (10–100; 100 = neprosojno). False = okna (še) ni ali ni Windows —
    kliči, ko je okno odprto (npr. iz `app.timer` ali ob prikazu)."""
    if user32 is None:
        if sys.platform != "win32":
            return False
        user32 = _user32()
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        return False
    alpha = round(255 * max(MIN_PERCENT, min(100, int(percent))) / 100)
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
    return bool(user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA))
