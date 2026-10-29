import subprocess
import sys
import uuid

import pytest

from pavzetest import single_instance


def test_show_request(tmp_path):
    assert single_instance.take_show_request(tmp_path) is False
    single_instance.request_show(tmp_path)
    assert single_instance.take_show_request(tmp_path) is True
    assert single_instance.take_show_request(tmp_path) is False


@pytest.mark.skipif(sys.platform != "win32", reason="mutex Windows")
def test_second_process_sees_running_instance():
    app_id = str(uuid.uuid4())
    assert single_instance.acquire(app_id) is True
    assert single_instance.acquire(app_id) is True            # isti proces znova
    probe = ("import sys; from pavzetest import single_instance as s; "
             f"sys.exit(0 if s.acquire('{app_id}') else 3)")
    assert subprocess.run([sys.executable, "-c", probe], timeout=60).returncode == 3
