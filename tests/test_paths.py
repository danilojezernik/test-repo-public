from pavzetest import paths
from pavzetest.identity import APP_NAME


def test_data_dir_override(tmp_path):
    paths.use(tmp_path / "drugje")
    assert paths.data_dir() == tmp_path / "drugje"
    assert (tmp_path / "drugje").is_dir()


def test_data_dir_default_under_appdata(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.use(None)
    assert paths.data_dir() == tmp_path / APP_NAME
