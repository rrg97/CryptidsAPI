from pathlib import Path
import os

if os.environ["CRYPTID_SQLITE_DB"] != ":memory:":
    SRC_DIR = Path(__file__).resolve().parent.parent
    DB_DIR_NAME = SRC_DIR / "db"

    os.environ["DB_NAME"] = "cryptid"
    DB_FILE = os.environ["DB_NAME"] + ".sqlite"
    os.environ["CRYPTID_SQLITE_DB"] = str(DB_DIR_NAME / DB_FILE)

from .creature import *
from .explorer import *