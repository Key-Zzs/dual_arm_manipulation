#!/usr/bin/env python
from __future__ import annotations
"""Perception debug placeholder."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bimanual_rule_control.perception.base import MockDetector


if __name__ == "__main__":
    for kind in ("tube", "rack", "hole"):
        result = MockDetector(kind).detect()
        print(f"{kind}: success={result.success} message={result.message}")
