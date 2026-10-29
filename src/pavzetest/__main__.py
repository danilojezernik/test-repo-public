"""Vstopna točka: `python -m pavzetest` (in konzolna skripta `pavzetest`)."""
import multiprocessing
import sys

from pavzetest.app import main

if __name__ in {"__main__", "__mp_main__"}:
    multiprocessing.freeze_support()      # zapakirana aplikacija: okno NiceGUI teče v podprocesu
    code = main()
    if code:                              # le napaka konča proces s kodo (testi NiceGUI tečejo v istem procesu)
        sys.exit(code)
