from pavzetest import window


class FakeUser32:
    def __init__(self, hwnd=42):
        self.hwnd, self.style, self.alpha = hwnd, 0x100, None

    def FindWindowW(self, cls, title):  # noqa: N802 — ime funkcije Win32
        return self.hwnd

    def GetWindowLongW(self, hwnd, index):  # noqa: N802
        return self.style

    def SetWindowLongW(self, hwnd, index, value):  # noqa: N802
        self.style = value

    def SetLayeredWindowAttributes(self, hwnd, key, alpha, flags):  # noqa: N802
        self.alpha = alpha
        return 1


def test_set_opacity_makes_layered_window():
    user32 = FakeUser32()
    assert window.set_opacity(60, user32=user32) is True
    assert user32.alpha == 153 and user32.style & window.WS_EX_LAYERED


def test_set_opacity_clamps():
    user32 = FakeUser32()
    window.set_opacity(0, user32=user32)
    assert user32.alpha == round(255 * window.MIN_PERCENT / 100)
    window.set_opacity(150, user32=user32)
    assert user32.alpha == 255


def test_set_opacity_without_window():
    assert window.set_opacity(50, user32=FakeUser32(hwnd=0)) is False
