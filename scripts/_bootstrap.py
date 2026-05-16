"""Script import path bootstrap."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap() -> Path:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    for path in (str(src), str(root)):
        if path not in sys.path:
            sys.path.insert(0, path)
    return root
