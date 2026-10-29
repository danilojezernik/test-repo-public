# DESKTOP.md — vodilo za namizno aplikacijo

Sklad: **Python ≥ 3.11**, **NiceGUI 3** (vmesnik, komponente Quasar), **pywebview 6** (namizno okno, EdgeChromium),
**SQLModel/SQLite** (lokalni podatki), **pytest** (+ NiceGUI `user`), **ruff**. Ciljni sistem: Windows 10/11.
Vsa besedila v vmesniku so **slovenska**.

## Struktura

```
src/pavzetest/
  __main__.py        vstop: python -m pavzetest
  app.py             zasloni, okno, zagon (ui.run), dimni zagon --smoke
  ui/                ZASLONI — vsak modul ima register() z @ui.page
  db.py, models.py   lokalna baza in nastavitve (Setting ključ/vrednost)
  paths.py           podatkovna mapa %APPDATA%\<ime> (nikoli ob kodi)
  single_instance.py en primerek; drugi zagon pokaže okno prvega
  autostart.py       samodejni zagon ob prijavi (HKCU\...\Run)
  window.py          prosojnost okna (set_opacity)
  identity.py        APP_NAME, APP_ID — Studiovo, NE UREJAJ
  _studio/           Studiov paket (različica, posodobitev) — NE UREJAJ
tests/               pytest; NiceGUI `user` za zaslone
```

## Ukazi (venv repoja — `python` je venv, ki ga ustvari Studio)

- `python -m pip install -e .[dev]` — pakete nameščaj le tako (okolje ima `PIP_REQUIRE_VIRTUALENV=1`).
- `python -m ruff check .` · `python -m pytest -q` · `python -m pavzetest --smoke` (brez okna, konča sam).
- `python -m pavzetest` odpre pravo okno — v teku ekipe ga ne zaganjaj (ne zapre se samo).

## Zasloni

- Vsak zaslon je modul v `ui/` s funkcijo `register()`, ki v sebi prijavi stran:

  ```python
  from nicegui import ui

  def register() -> None:
      @ui.page("/")
      def glavna() -> None:
          ui.label("…")
  ```

  `ui.register_all()` jih prijavi ob vsakem zagonu. Dekorator na ravni modula NE — NiceGUI testi po vsakem testu
  pobrišejo poti in stran bi v naslednjem testu izginila. Nadomestna stran `/` v `app.py` se umakne sama, ko
  zaslon v `ui/` prijavi `/`.
- Nikoli sinhrono delo z diskom ali omrežjem v obdelavi dogodka — `await run.io_bound(funkcija, …)` (sicer okno
  zamrzne, „Connection lost").
- NiceGUI 3 pasti: `classes(replace=…)` na `ui.row`/`ui.column` izbriše razred `nicegui-row`/`nicegui-column` (raje
  `classes(add=…, remove=…)`); Quasarjevi `!important` razredi (`text-primary`) premagajo lastne — gumbu z lastno
  barvo daj `color=None`.

## Okno (pywebview prek NiceGUI)

- Ob zagonu: `app.native.window_args` (`frameless`, `on_top`, `hidden`, `min_size`) in argumenti
  `ui.run(window_size=…, fullscreen=…)`. Po zagonu: `app.native.main_window` — `show()`, `hide()`, `restore()`,
  `minimize()`, `toggle_fullscreen()`, `set_always_on_top(True)`, `resize(w, h)`, `move(x, y)`.
- Okno teče v **podprocesu** (`multiprocessing`, spawn): v podproces ne pošiljaj objektov, ki se ne dajo
  serializirati; `main()` se v podprocesu takoj vrne.
- **Prosojno ozadje** (npr. pavza čez cel zaslon): `window.set_opacity(70)` — prosojnost CELEGA okna (10–100 %,
  100 = neprosojno), kliči, ko je okno odprto (npr. ob prikazu pavze), in nazaj na 100 za nastavitve.
  **`app.native.window_args["transparent"] = True` NE uporabljaj** — pywebview 6.2 na Windows z njim namizja ne
  pokaže (preizkus 2026-10-29). Prosojno je tudi besedilo: krepka, velika pisava in dober kontrast; ozadje strani
  polna barva (prosojnost da okno).
- Delo v ozadju (časovniki, opomniki): `app.timer(sekunde, funkcija)` (na ravni aplikacije, ne strani); stanje v
  `db`, ne v globalnih spremenljivkah.

## Podatki in viri

- Podatki in nastavitve: `db.get_setting` / `db.set_setting` ali nove tabele v `models.py` (SQLModel). Datoteke v
  `paths.data_dir()`.
- Datoteke paketa (slike, pisave, zvoki) beri z `importlib.resources.files("pavzetest") / "viri" / …`
  — deluje tudi v zapakirani aplikaciji (relativne poti in `__file__` ne).
- Pisave in slike so lokalno v paketu (ne CDN): aplikacija mora delati brez interneta.

## Namestitev (gradi Studio)

- Namestitveni program `<Ime>-<različica>-setup.exe` zgradi Studio z gumbom „Zgradi namestitev" iz **zadnjega
  commita** veje dela — neoddane datoteke (`.env`) niso vključene. Recept (PyInstaller, Inno Setup) je Studiov: v
  repoju ni skripte gradnje ne `.spec`.
- Projekt poda le podatke v `pyproject.toml` → `[tool.studio]`: `ime` (ime v meniju Start; privzeto `APP_NAME`) in
  `ikona` (pot do `.ico` v repoju). Ime: črke, števke, presledek in `. ( ) + & ' - _`, največ 60 znakov.
- V aplikacijo pride **ves paket** `src/pavzetest/` (koda in viri v `viri/`) brez testov in `.studio/`;
  datoteke zunaj paketa ne. Vire beri z `importlib.resources` (zgoraj).
- `_studio/` in vstop zapakirane aplikacije sta Studiova — gradnja ju prepiše.
- Gradnja zažene zapakirano aplikacijo z `--smoke` — dimni zagon mora delati tudi zapakiran: brez poti iz `__file__`,
  brez konzole (`print` gre v prazno), podatki le v `paths.data_dir()` (nameščena mapa je le za branje).
- Nameščena aplikacija teče brez skrbniških pravic (`%LOCALAPPDATA%\Programs\<Ime>`); en primerek
  (`single_instance`) je pogoj, da namestitev nove različice počaka na zaprtje aplikacije.

## Testi

- Logika: navaden pytest (baza v začasni mapi — `tests/conftest.py`).
- Zasloni: `async def test_…(user: User)` → `await user.open("/")`, `await user.should_see("…")`,
  `user.find("Shrani").click()`.
- Samodejni zagon in register: lažen register (`tests/test_autostart.py`), nikoli pravi `HKCU` v testih.
