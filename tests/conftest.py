# tests/conftest.py

import sys
from pathlib import Path

# 将项目根（包含 app/）加入到 sys.path
ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
