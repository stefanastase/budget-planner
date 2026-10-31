from budget_planner.models import Budget, Expense, Month, SavedExpense


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


def test_saved_expense_to_expense_with_override():
    s = SavedExpense("Netflix", "Fun", 13.99, "sub")
    assert s.to_expense("2026-10-05") == Expense("2026-10-05", "Fun", 13.99, "sub")
    assert s.to_expense("2026-10-05", 15).amount == 15


def test_save_expense_replaces_same_name_case_insensitive():
    b = Budget()
    b.save_expense(SavedExpense("Netflix", "Fun", 13.99))
    b.save_expense(SavedExpense("netflix", "Fun", 15.99))
    assert len(b.saved) == 1 and b.saved[0].amount == 15.99


def test_budget_roundtrip_with_saved_and_old_files():
    b = Budget(saved=[SavedExpense("Rent", "Rent", 900)])
    assert Budget.from_dict(b.to_dict()) == b
    assert Budget.from_dict({"months": {}}).saved == []
