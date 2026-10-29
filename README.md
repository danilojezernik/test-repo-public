# pavze-test

Namizna aplikacija za Windows — Python, NiceGUI (vmesnik), pywebview (okno), SQLModel/SQLite (lokalni podatki).

## Zagon iz kode

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e .[dev]
.venv\Scripts\python.exe -m pavzetest
```

## Preverba

```powershell
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pavzetest --smoke
```

Podatki in nastavitve so v `%APPDATA%\pavze-test`. Navodila za razvoj: `DESKTOP.md`.

Smoke izdaj: po v1.0.0.

Smoke izdaj: po v1.0.2.

smoke posodobitve A

smoke posodobitve B

smoke posodobitve A
