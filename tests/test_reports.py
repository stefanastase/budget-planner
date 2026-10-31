from budget_planner.models import Expense, Month
from budget_planner.reports import render, summarize


def make_month():
    return Month(
        income=2500,
        budgets={"Rent": 900, "Food": 300},
        expenses=[
            Expense("2026-10-01", "Rent", 850.5),
            Expense("2026-10-03", "Food", 200),
            Expense("2026-10-09", "Food", 140),
            Expense("2026-10-10", "Fun", 25),
        ],
    )


def test_totals():
    s = summarize(make_month())
    assert s.planned == 1200
    assert s.spent == 1215.5
    assert s.remaining == 1284.5


def test_over_budget_and_unbudgeted():
    s = summarize(make_month())
    food = next(ln for ln in s.lines if ln.name == "Food")
    assert food.spent == 340 and food.over
    assert s.unbudgeted == {"Fun": 25}


def test_overplanned():
    m = Month(income=100, budgets={"A": 150})
    assert summarize(m).overplanned == 50


def test_render_mentions_over_budget():
    text = render(summarize(make_month()), "2026-10")
    assert "OVER BUDGET" in text and "Fun" in text
