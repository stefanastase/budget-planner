"""Reading and writing the budget to a JSON file."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Budget


def default_path() -> Path:
    override = os.environ.get("BUDGET_DATA_FILE")
    if override:
        return Path(override)
    return Path.home() / ".budget_planner" / "data.json"


def load(path: Path | None = None) -> Budget:
    path = path or default_path()
    if not path.exists():
        return Budget()
    return Budget.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save(budget: Budget, path: Path | None = None) -> None:
    path = path or default_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(budget.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
