"""Testi tečejo v začasni podatkovni mapi — nikoli v pravi `%APPDATA%`."""
import pytest

from pavzetest import db, paths


@pytest.fixture(autouse=True)
def _podatki(tmp_path):
    paths.use(tmp_path / "podatki")
    db.reset()
    yield
    db.reset()
    paths.use(None)
