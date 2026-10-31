"""Summary calculations (pure functions) and text rendering."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Month, SavedExpense


@dataclass
class CategoryLine:
    name: str
    budget: float
    spent: float

    @property
    def percent(self) -> float:
        if self.budget:
            return self.spent / self.budget * 100
        return 100.0 if self.spent else 0.0

    @property
    def over(self) -> bool:
        return self.spent > self.budget


@dataclass
class Summary:
    income: float
    planned: float
    spent: float
    lines: list[CategoryLine] = field(default_factory=list)
    unbudgeted: dict[str, float] = field(default_factory=dict)

    @property
    def remaining(self) -> float:
        return self.income - self.spent

    @property
    def overplanned(self) -> float:
        """How much the category budgets exceed income (0 if they don't)."""
        return max(0.0, self.planned - self.income)


def summarize(month: Month) -> Summary:
    spent: dict[str, float] = {}
    for e in month.expenses:
        spent[e.category] = spent.get(e.category, 0.0) + e.amount

    lines = [CategoryLine(c, b, spent.pop(c, 0.0)) for c, b in month.budgets.items()]
    return Summary(
        income=month.income,
        planned=sum(month.budgets.values()),
        spent=sum(e.amount for e in month.expenses),
        lines=lines,
        unbudgeted=spent,
    )


def money(x: float, currency: str = "€") -> str:
    return f"{x:,.2f} {currency}"


def render(summary: Summary, month_key: str, currency: str = "€") -> str:
    def m(x: float) -> str:
        return money(x, currency)

    out = [
        f"\n=== Summary for {month_key} ===",
        f"Income:           {m(summary.income)}",
        f"Planned budget:   {m(summary.planned)}",
        f"Spent so far:     {m(summary.spent)}",
        f"Left to spend:    {m(summary.remaining)}",
    ]
    if summary.overplanned:
        out.append(f"  ! Budgets exceed income by {m(summary.overplanned)}")
    out.append("")

    for ln in summary.lines:
        filled = min(int(ln.percent / 5), 20)
        bar = "#" * filled + "-" * (20 - filled)
        flag = "  OVER BUDGET" if ln.over else ""
        out.append(
            f"{ln.name:<14} [{bar}] {ln.percent:5.0f}%  {m(ln.spent)} / {m(ln.budget)}{flag}"
        )
    for cat, s in summary.unbudgeted.items():
        out.append(f"{cat:<14} (no budget)  {m(s)}")
    return "\n".join(out) + "\n"


def render_saved(saved: list[SavedExpense], currency: str = "€") -> str:
    """A boxed, titled table of the saved expenses ('' if there are none)."""
    if not saved:
        return ""
    title = f"Saved expenses ({len(saved)})"
    header = ("#", "Name", "Category", "Amount", "Note")
    rows = [
        (str(i), s.name, s.category, money(s.amount, currency), s.note)
        for i, s in enumerate(saved, 1)
    ]
    w = [max(len(r[c]) for r in [header, *rows]) for c in range(5)]

    def fmt(r: tuple) -> str:
        cells = [r[0].rjust(w[0]), r[1].ljust(w[1]), r[2].ljust(w[2]), r[3].rjust(w[3]), r[4]]
        return "  ".join(cells).rstrip()

    body = [fmt(header), "─" * max(len(fmt(header)), *(len(fmt(r)) for r in rows)), *map(fmt, rows)]
    inner = max(len(title) + 1, *(len(line) for line in body))
    lines = ["┌─ " + title + " " + "─" * (inner - len(title) - 1) + "┐"]
    lines += ["│ " + line.ljust(inner) + " │" for line in body]
    lines.append("└" + "─" * (inner + 2) + "┘")
    return "\n".join(lines)
