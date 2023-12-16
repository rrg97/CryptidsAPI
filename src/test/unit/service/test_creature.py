from service import creature as code
from model import Creature

sample = Creature(
    name="Yeti",
    country="CN",
    area="Himalayas",
    description="Hirsute Himalayan",
    aka="Abominable Snowman"
)

def test_create():
    resp = code.create(sample)

def test_get_exists():
    resp = code.get_one("Yeti")
    assert resp == sample

def test_get_missing():
    resp = code.get_one("boxturtle")
    assert resp is None