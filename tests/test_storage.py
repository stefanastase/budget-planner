from budget_planner import storage
from budget_planner.models import Budget, Expense


def test_save_and_load(tmp_path):
    path = tmp_path / "sub" / "data.json"
    b = Budget()
    m = b.get_month("2026-10")
    m.income = 2000
    m.budgets["Food"] = 300
    m.expenses.append(Expense("2026-10-05", "Food", 42.0))
    storage.save(b, path)
    assert storage.load(path) == b


def test_load_missing_file_returns_empty(tmp_path):
    assert storage.load(tmp_path / "nope.json") == Budget()


def test_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("BUDGET_DATA_FILE", str(tmp_path / "x.json"))
    assert storage.default_path() == tmp_path / "x.json"
