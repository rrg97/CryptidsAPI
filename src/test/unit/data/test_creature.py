import os
import pytest
from model.creature import Creature

os.environ["CRYPTID_SQLITE_DB"] = ":memory:"

from data.errors import MissingException, DuplicateException
from src.data.creature import create, get_one, modify, delete

@pytest.fixture
def sample() -> Creature:
    return Creature(
        name="yeti",
        description="Harmless Himalayan",
        country="CN",
        area="Himalayas",
        aka="Abominable Snowman"
    )

def test_create(sample):
    resp = create(sample)

    assert resp == sample

def test_create_duplicate(sample):
    with pytest.raises(DuplicateException) as ex:
        _ = create(sample)
    
    assert f"Creature {sample.name} already exists" in str(ex.value)

def test_get_one(sample):
    resp = get_one(sample.name)

    assert resp == sample

def test_get_one_missing(sample):
    with pytest.raises(MissingException) as ex:
        _ = get_one(name="Pepita")
    
    assert str(ex.value) == f"Creature {sample.name} not found"

def test_modify(sample):
    sample.area = "Sesame Street"
    resp = modify(creature=sample)

    assert resp == sample

def test_modify_missing(sample):
    sample.area = "Sesame Street"
    with pytest.raises(MissingException) as ex:
        _ = modify(sample)
    
    assert str(ex.value) == f"Creature {sample.name} not found"

def test_delete(sample):
    resp = delete(sample.name)

    assert resp == True

def test_delete_missing(sample):
    with pytest.raises(MissingException) as excinfo:
        _ = delete(sample.name)
    
    assert str(excinfo.value) == 'Creature yeti not found' 