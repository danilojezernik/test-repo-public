"""En primerek aplikacije. Windows: poimenovan mutex `Local\\<APP_ID>` (isto ime uporabi namestitveni program, da ob
posodobitvi počaka na zaprtje aplikacije). Drugi zagon prosi prvega, naj pokaže okno (datoteka v podatkovni mapi)."""
from __future__ import annotations

import sys
from pathlib import Path

ERROR_ALREADY_EXISTS = 183
SHOW_REQUEST = "pokazi-okno.zahteva"

_held: dict[str, int] = {}          # ime mutexa -> ročaj (živi do konca procesa)


def mutex_name(app_id: str) -> str:
    return f"Local\\{app_id}"


def acquire(app_id: str) -> bool:
    """True = ta proces je edini primerek; False = aplikacija že teče. Isti proces znova → True."""
    name = mutex_name(app_id)
    if name in _held or sys.platform != "win32":
        return True
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel32.CreateMutexW(None, False, name)
    if not handle:                  # mutexa ni mogoče ustvariti: teci brez zaščite pred dvojnim zagonom
        return True
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False
    _held[name] = handle
    return True


def request_show(data_dir: Path) -> None:
    """Drugi zagon: prvi primerek naj pokaže svoje okno."""
    (Path(data_dir) / SHOW_REQUEST).touch()


def take_show_request(data_dir: Path) -> bool:
    """Prvi primerek (časovnik): ali je drugi zagon prosil za okno — zahteva se ob branju pobriše."""
    try:
        (Path(data_dir) / SHOW_REQUEST).unlink()
    except OSError:
        return False
    return True
