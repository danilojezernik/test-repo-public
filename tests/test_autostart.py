import sys

from pavzetest import autostart
from pavzetest.identity import APP_NAME


class FakeRegistry:
    def __init__(self):
        self.values: dict[str, str] = {}

    def get(self, name):
        return self.values.get(name)

    def set(self, name, value):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)


def test_enable_disable():
    reg = FakeRegistry()
    assert autostart.is_enabled(registry=reg) is False
    autostart.enable('"C:\\app.exe"', registry=reg)
    assert reg.values == {APP_NAME: '"C:\\app.exe"'} and autostart.is_enabled(registry=reg)
    autostart.disable(registry=reg)
    assert autostart.is_enabled(registry=reg) is False
    autostart.disable(registry=reg)                 # že izklopljeno: brez napake


def test_launch_command_from_source():
    command = autostart.launch_command()
    assert command.endswith(f" -m {autostart.__name__.partition('.')[0]}")


def test_launch_command_frozen(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert autostart.launch_command() == f'"{sys.executable}"'
