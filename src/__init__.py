from pathlib import Path
import sys

parent = Path(__file__).parent.resolve()
sys.path.append(
    str(parent)
)
