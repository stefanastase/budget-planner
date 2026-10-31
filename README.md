# Budget Planner

A small terminal app for monthly budget planning: set your income, define
category budgets, log expenses and see how much you have left.

## Features

- Monthly income and per-category budgets
- Expense log per category
- **Saved expenses**: keep reusable entries (Rent, Netflix, ...) and add one or several straight from the Add expense menu
- Summary with progress bars and over-budget warnings

## Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
budget                 # or: python -m budget_planner
```

Data is stored in `~/.budget_planner/data.json`. Set the `BUDGET_DATA_FILE`
environment variable to use a different file.

## Test

```bash
pytest
ruff check .
```

## Layout

| Module | Responsibility |
|---|---|
| `models.py`  | `Expense`, `SavedExpense`, `Month`, `Budget` data classes |
| `storage.py` | Load/save JSON |
| `reports.py` | Summary calculations and text rendering |
| `cli.py`     | Menu and user input |
