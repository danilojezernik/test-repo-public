"""Podatkovna mapa uporabnika: podatki in nastavitve nikoli ob kodi (nameščena aplikacija je le za branje)."""
from __future__ import annotations

import os
from pathlib import Path

from pavzetest.identity import APP_NAME

_override: Path | None = None


def use(path: Path | None) -> None:
    """Druga podatkovna mapa (`--data-dir`, testi); None = privzeta `%APPDATA%\\<APP_NAME>`."""
    global _override
    _override = Path(path) if path is not None else None


def data_dir() -> Path:
    """Podatkovna mapa (ustvari jo, če je ni)."""
    if _override is not None:
        base = _override
    else:
        roaming = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        base = Path(roaming) / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base
