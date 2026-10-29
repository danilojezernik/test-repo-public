"""Zasloni aplikacije: vsak modul v tej mapi ima funkcijo `register()`, v kateri prijavi svoje strani (`@ui.page`).
`register_all()` jih prijavi ob VSAKEM zagonu — tudi v testih NiceGUI, ki po vsakem testu pobrišejo poti
(dekorator na ravni modula bi se izvedel le ob prvem uvozu)."""
from __future__ import annotations

import importlib
import pkgutil


def register_all() -> None:
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{__name__}.{info.name}")
        register = getattr(module, "register", None)
        if callable(register):
            register()
