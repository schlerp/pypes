import os
import tempfile
from uuid import uuid4

from pypes.models import Resource


def test_resource_path():
    assert "/test/path" == Resource(path="/test/path").path


def test_resource_id_default():
    assert Resource(path="/test/path").id is not None


def test_resource_id():
    _id = uuid4()
    assert Resource(path="/test/path", id=_id).id == _id


def test_resource_exist():
    with tempfile.NamedTemporaryFile() as f:
        res = Resource(path=f.name)
        assert res.exists


def test_resource_no_exist():
    assert not Resource(path="i/should/definitely/not/exist").exists
