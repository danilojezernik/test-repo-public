"""Lokalna baza (SQLite v podatkovni mapi uporabnika) in nastavitve ključ/vrednost."""
from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from pavzetest import paths
from pavzetest.models import Setting

DB_NAME = "podatki.sqlite"
_engine: Engine | None = None


def init() -> Engine:
    """Baza v podatkovni mapi (ustvari tabele ob prvem klicu)."""
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{(paths.data_dir() / DB_NAME).as_posix()}")
        SQLModel.metadata.create_all(_engine)
    return _engine


def reset() -> None:
    """Zapri bazo (druga podatkovna mapa, testi)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def get_setting(key: str, default: str | None = None) -> str | None:
    with Session(init()) as session:
        row = session.get(Setting, key)
        return row.value if row is not None else default


def set_setting(key: str, value: str) -> None:
    with Session(init()) as session:
        row = session.get(Setting, key) or Setting(key=key, value=value)
        row.value = value
        session.add(row)
        session.commit()
