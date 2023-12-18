import os
import pytest
from model.explorer import Explorer

os.environ["CRYPTID_SQLITE_DB"] = ":memory:"

from data.errors import MissingException, DuplicateException
from src.data.explorer import create, get_one, modify, delete

@pytest.fixture
def sample() -> Explorer:
    return Explorer(
        name="Jean Cousteau",
        country="FR",
        description="Just a curious guy"
    )

def test_create(sample):
    resp = create(sample)

    assert resp == sample

def test_create_duplicate(sample):
    with pytest.raises(DuplicateException) as ex:
        _ = create(sample)
    
    assert f"Explorer {sample.name} already exists" in str(ex.value)

def test_get_one(sample):
    resp = get_one(sample.name)

    assert resp == sample

def test_get_one_missing(sample):
    with pytest.raises(MissingException) as ex:
        _ = get_one(name="Pepita")
    
    assert str(ex.value) in f"Explorer {sample.name} not found"

def test_modify(sample):
    sample.country = "US"
    resp = modify(explorer=sample)

    assert resp == sample

def test_modify_missing(sample):
    sample.country = "US"
    with pytest.raises(MissingException) as ex:
        _ = modify(sample)
    
    assert str(ex.value) == f"Explorer {sample.name} not found"

def test_delete(sample):
    resp = delete(sample.name)

    assert resp == True

def test_delete_missing(sample):
    with pytest.raises(MissingException) as excinfo:
        _ = delete(sample.name)
    
    assert str(excinfo.value) == f'Explorer {sample.name} not found' 