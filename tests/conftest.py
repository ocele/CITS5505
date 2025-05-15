# tests/conftest.py

import sys
from pathlib import Path

# Add the project root directory (which contains app/) to sys.path
ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
