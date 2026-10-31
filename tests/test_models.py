from budget_planner.models import Budget, Expense, Month


def test_month_roundtrip():
    m = Month(
        income=2500,
        budgets={"Rent": 900},
        expenses=[Expense("2026-10-01", "Rent", 850.5, "Oct")],
    )
    assert Month.from_dict(m.to_dict()) == m


def test_get_month_creates_and_reuses():
    b = Budget()
    first = b.get_month("2026-10")
    first.income = 100
    assert b.get_month("2026-10").income == 100
