# tests/conftest.py
import sys
from pathlib import Path

# Add the project root (parent of this tests/ folder) to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
