"""Plain data classes; no input/output in here."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Expense:
    date: str  # ISO format, YYYY-MM-DD
    category: str
    amount: float
    note: str = ""


@dataclass
class Month:
    income: float = 0.0
    budgets: dict[str, float] = field(default_factory=dict)
    expenses: list[Expense] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "income": self.income,
            "budgets": dict(self.budgets),
            "expenses": [asdict(e) for e in self.expenses],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Month:
        return cls(
            income=float(data.get("income", 0.0)),
            budgets={k: float(v) for k, v in data.get("budgets", {}).items()},
            expenses=[Expense(**e) for e in data.get("expenses", [])],
        )


@dataclass
class Budget:
    """All months, keyed by 'YYYY-MM'."""

    months: dict[str, Month] = field(default_factory=dict)

    def get_month(self, key: str) -> Month:
        return self.months.setdefault(key, Month())

    def to_dict(self) -> dict:
        return {"months": {k: m.to_dict() for k, m in self.months.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> Budget:
        return cls(months={k: Month.from_dict(m) for k, m in data.get("months", {}).items()})
