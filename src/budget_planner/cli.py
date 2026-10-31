"""Interactive terminal menu."""

from __future__ import annotations

from datetime import date

from . import storage
from .models import Expense, Month
from .reports import money, render, summarize

MENU = """
1. Set monthly income
2. Add / update budget category
3. Add expense
4. List expenses
5. Delete expense
6. Show summary
7. Switch month
0. Quit"""


# ---------- input helpers ----------
def ask_amount(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
            if value < 0:
                raise ValueError
            return round(value, 2)
        except ValueError:
            print("  Please enter a positive number.")


def ask_date(month_key: str) -> str:
    while True:
        raw = input("Date YYYY-MM-DD (Enter = today): ").strip()
        if not raw:
            today = date.today().isoformat()
            return today if today.startswith(month_key) else f"{month_key}-01"
        try:
            date.fromisoformat(raw)
        except ValueError:
            print("  Invalid date.")
            continue
        if not raw.startswith(month_key):
            print(f"  Date must be within {month_key}.")
            continue
        return raw


def pick_category(month: Month) -> str | None:
    cats = list(month.budgets)
    if not cats:
        print("  No categories yet. Add a budget category first (option 2).")
        return None
    for i, c in enumerate(cats, 1):
        print(f"  {i}. {c}")
    while True:
        raw = input("Category number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(cats):
            return cats[int(raw) - 1]
        print("  Invalid choice.")


# ---------- actions ----------
def set_income(month: Month) -> None:
    month.income = ask_amount("Monthly income: ")
    print(f"  Income set to {money(month.income)}")


def set_budget(month: Month) -> None:
    name = input("Category name (e.g. Rent, Food): ").strip().title()
    if not name:
        return
    month.budgets[name] = ask_amount(f"Budget for {name}: ")
    print(f"  {name}: {money(month.budgets[name])}")


def add_expense(month: Month, month_key: str) -> None:
    cat = pick_category(month)
    if not cat:
        return
    amount = ask_amount("Amount: ")
    note = input("Note (optional): ").strip()
    month.expenses.append(Expense(ask_date(month_key), cat, amount, note))
    print("  Expense added.")


def list_expenses(month: Month) -> list[Expense]:
    ordered = sorted(month.expenses, key=lambda e: e.date)
    if not ordered:
        print("  No expenses yet.")
    for i, e in enumerate(ordered, 1):
        print(f"  {i:>2}. {e.date}  {e.category:<14} {money(e.amount):>14}  {e.note}")
    return ordered


def delete_expense(month: Month) -> None:
    ordered = list_expenses(month)
    if not ordered:
        return
    raw = input("Number to delete (Enter = cancel): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(ordered):
        month.expenses.remove(ordered[int(raw) - 1])
        print("  Deleted.")


def change_month(current: str) -> str:
    raw = input("Month as YYYY-MM (Enter = this month): ").strip()
    if not raw:
        return date.today().strftime("%Y-%m")
    try:
        date.fromisoformat(raw + "-01")
        return raw
    except ValueError:
        print(f"  Invalid format, keeping {current}")
        return current


# ---------- main loop ----------
def main() -> None:
    budget = storage.load()
    month_key = date.today().strftime("%Y-%m")
    print("Monthly Budget Planner")

    try:
        while True:
            month = budget.get_month(month_key)
            print(f"\n--- {month_key} ---{MENU}")
            choice = input("> ").strip()

            if choice == "1":
                set_income(month)
            elif choice == "2":
                set_budget(month)
            elif choice == "3":
                add_expense(month, month_key)
            elif choice == "4":
                list_expenses(month)
            elif choice == "5":
                delete_expense(month)
            elif choice == "6":
                print(render(summarize(month), month_key))
            elif choice == "7":
                month_key = change_month(month_key)
            elif choice == "0":
                break
            else:
                print("  Unknown option.")
            storage.save(budget)
    except (KeyboardInterrupt, EOFError):
        print()
    storage.save(budget)
    print("Saved. Bye!")


if __name__ == "__main__":
    main()
