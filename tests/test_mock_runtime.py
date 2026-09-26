import datetime
import random
import tempfile
import time
import types
import uuid
from pathlib import Path

from tools.mock_runtime import bind, bind_determinism


def test_mock_filesystem_cannot_delete_host_file():
    sandbox_open, mock_os, _, _, _ = bind("case_a")
    with tempfile.NamedTemporaryFile() as host_file:
        assert mock_os.path.exists(host_file.name) is False
        with sandbox_open(host_file.name, "w") as mock_file:
            mock_file.write("mock")
        assert mock_os.path.exists(host_file.name)
        mock_os.remove(host_file.name)
        assert Path(host_file.name).exists()


def test_mock_filesystem_rejects_parent_traversal():
    _, mock_os, _, _, _ = bind("case_b")
    try:
        mock_os.path.exists("../../outside")
    except ValueError:
        pass
    else:
        raise AssertionError("parent traversal escaped the mock sandbox")


def test_mock_time_and_ids_repeat_on_fresh_load():
    def create_module():
        module = types.SimpleNamespace(random=random, time=time, uuid=uuid, datetime=datetime)
        bind_determinism(module)
        return module

    first, second = create_module(), create_module()
    assert first.random.randint(1, 100) == second.random.randint(1, 100)
    assert first.uuid.uuid4() == second.uuid.uuid4()
    assert first.datetime.datetime.now() == second.datetime.datetime.now()
    first.time.sleep(3)
    assert first.time.time() > second.time.time()
