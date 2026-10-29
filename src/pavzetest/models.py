"""Tabele lokalne baze (SQLModel)."""
from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    """Nastavitev aplikacije kot ključ/vrednost (vrednost je besedilo; JSON za sestavljene)."""
    key: str = Field(primary_key=True)
    value: str
