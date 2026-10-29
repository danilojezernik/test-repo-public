"""Aplikacija: zasloni, okno in zagon (NiceGUI za vmesnik, pywebview za okno)."""
from __future__ import annotations

import argparse
import multiprocessing
import os
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from nicegui import app, background_tasks, helpers, native, run, ui

from pavzetest import db, paths, single_instance
from pavzetest import ui as screens
from pavzetest._studio import update
from pavzetest.identity import APP_ID, APP_NAME

WINDOW_SIZE = (1100, 720)
SMOKE_TIMEOUT_S = 60        # dimni zagon (gate Studia) se konča sam, tudi če stran ne odgovori


def register_pages() -> None:
    """Zasloni iz `ui/` (vsak modul s funkcijo `register()`); dokler ni strani `/`, nadomestna stran skeleta."""
    screens.register_all()
    if not any(getattr(route, "path", None) == "/" for route in app.routes):
        @ui.page("/")
        def _zacetek() -> None:          # NADOMESTNA stran — prvi zaslon v ui/ jo zamenja
            ui.label(APP_NAME).classes("text-2xl font-semibold")
            ui.label("Aplikacija je pripravljena.")


def _args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=APP_NAME)
    parser.add_argument("--smoke", action="store_true", help="dimni zagon brez okna (preverba Studia)")
    parser.add_argument("--data-dir", type=Path, help="druga podatkovna mapa (namesto %%APPDATA%%)")
    return parser.parse_known_args(argv)[0]


def _show_if_requested() -> None:
    """Drugi zagon je prosil za okno (single_instance) — pokaži okno prvega primerka."""
    if single_instance.take_show_request(paths.data_dir()) and app.native.main_window is not None:
        app.native.main_window.show()
        app.native.main_window.restore()


def _status(url: str) -> int:
    """HTTP status strani; strežnik se šele zaganja → nekaj ponovitev."""
    for _ in range(40):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            return exc.code
        except OSError:
            time.sleep(0.25)
    return 0


def _smoke() -> int:
    """Strežnik brez okna in brskalnika, zahteva `/`, konec: 0 = stran odgovori 200."""
    os.environ.pop("PYTEST_CURRENT_TEST", None)     # zagnan iz testa: NiceGUI bi sicer čakal testna vrata
    port = native.find_open_port()
    result = {"ok": False}
    guard = threading.Timer(SMOKE_TIMEOUT_S, lambda: os._exit(1))
    guard.daemon = True
    guard.start()

    async def check() -> None:
        try:
            result["ok"] = await run.io_bound(_status, f"http://127.0.0.1:{port}/") == 200
        finally:
            app.shutdown()

    app.on_startup(lambda: background_tasks.create(check()))     # po zagonu, ne med njim
    ui.run(native=False, show=False, reload=False, host="127.0.0.1", port=port, title=APP_NAME)
    guard.cancel()
    return 0 if result["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    if multiprocessing.current_process().name != "MainProcess":
        return 0                             # podproces okna (pywebview) ne zažene aplikacije znova
    args = _args([] if helpers.is_user_simulation() else argv)
    if args.smoke and args.data_dir is None:     # gate Studia: nikoli v pravo podatkovno mapo uporabnika
        args.data_dir = Path(tempfile.mkdtemp(prefix="smoke-"))
    if args.data_dir is not None:
        paths.use(args.data_dir)
    db.init()
    register_pages()
    update.start(app)
    if args.smoke:
        return _smoke()
    if not helpers.is_user_simulation():
        if not single_instance.acquire(APP_ID):
            single_instance.request_show(paths.data_dir())
            return 0
        app.timer(1.0, _show_if_requested)
    ui.run(native=True, reload=False, port=native.find_open_port(), title=APP_NAME, window_size=WINDOW_SIZE)
    return 0
