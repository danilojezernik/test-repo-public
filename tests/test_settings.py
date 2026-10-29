from pavzetest import db


def test_setting_roundtrip():
    assert db.get_setting("interval", "30") == "30"
    db.set_setting("interval", "45")
    db.set_setting("interval", "50")
    assert db.get_setting("interval") == "50"
