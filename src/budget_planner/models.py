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
class SavedExpense:
    """A reusable expense template (e.g. 'Netflix'), kept across months."""

    name: str
    category: str
    amount: float
    note: str = ""

    def to_expense(self, day: str, amount: float | None = None) -> Expense:
        return Expense(day, self.category, self.amount if amount is None else amount, self.note)


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
    saved: list[SavedExpense] = field(default_factory=list)

    def get_month(self, key: str) -> Month:
        return self.months.setdefault(key, Month())

    def save_expense(self, item: SavedExpense) -> None:
        """Add to the saved list; an existing entry with the same name is replaced."""
        for i, s in enumerate(self.saved):
            if s.name.casefold() == item.name.casefold():
                self.saved[i] = item
                return
        self.saved.append(item)

    def to_dict(self) -> dict:
        return {
            "months": {k: m.to_dict() for k, m in self.months.items()},
            "saved": [asdict(s) for s in self.saved],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Budget:
        return cls(
            months={k: Month.from_dict(m) for k, m in data.get("months", {}).items()},
            saved=[SavedExpense(**s) for s in data.get("saved", [])],
        )
