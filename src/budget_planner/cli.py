"""Interactive terminal menu."""

from __future__ import annotations

from datetime import date

from . import storage
from .models import Budget, Expense, Month, SavedExpense
from .reports import money, render, render_saved, summarize

MENU = """
1. Set monthly income
2. Add / update budget category
3. Add expense (new or from saved list)
4. Manage saved list
5. List expenses
6. Delete expense
7. Show summary
8. Switch month
0. Quit"""


# ---------- input helpers ----------
def ask_amount(prompt: str, default: float | None = None) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        if not raw and default is not None:
            return default
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


def add_expense(budget: Budget, month: Month, month_key: str) -> None:
    """Entry point for option 3: pick from the saved list, or enter a new expense."""
    if budget.saved:
        print_saved(budget)
        raw = input("Saved number(s), e.g. 1 or 1,3 (Enter = new expense): ").strip()
        if raw:
            add_from_saved(budget, month, month_key, raw)
            return
    add_new_expense(budget, month, month_key)


def add_new_expense(budget: Budget, month: Month, month_key: str) -> None:
    cat = pick_category(month)
    if not cat:
        return
    amount = ask_amount("Amount: ")
    note = input("Note (optional): ").strip()
    month.expenses.append(Expense(ask_date(month_key), cat, amount, note))
    print("  Expense added.")
    if input("Save to your saved list for reuse? [y/N]: ").strip().lower() == "y":
        name = input("Name (e.g. Netflix): ").strip()
        if name:
            budget.save_expense(SavedExpense(name, cat, amount, note))
            print(f"  Saved '{name}'.")


def print_saved(budget: Budget) -> bool:
    if not budget.saved:
        print("  Your saved list is empty.")
        return False
    print(render_saved(budget.saved))
    return True


def add_from_saved(budget: Budget, month: Month, month_key: str, raw: str) -> None:
    """Add the saved entries named by comma-separated list numbers in `raw`."""
    chosen: list[SavedExpense] = []
    for part in raw.split(","):
        part = part.strip()
        if not (part.isdigit() and 1 <= int(part) <= len(budget.saved)):
            print(f"  Invalid choice '{part}'. Nothing added.")
            return
        chosen.append(budget.saved[int(part) - 1])
    day = ask_date(month_key)
    for s in chosen:
        amount = ask_amount(f"{s.name} amount [{money(s.amount)}] (Enter = keep): ", s.amount)
        month.expenses.append(s.to_expense(day, amount))
        if s.category not in month.budgets:
            print(f"  Note: '{s.category}' has no budget this month (shown as 'no budget').")
    print(f"  Added {len(chosen)} expense(s).")


def manage_saved(budget: Budget) -> None:
    print_saved(budget)
    choice = input("[n]ew, [d]elete, Enter = back: ").strip().lower()
    if choice == "n":
        name = input("Name (e.g. Rent, Netflix): ").strip()
        category = input("Category: ").strip().title()
        if not name or not category:
            return
        amount = ask_amount("Amount: ")
        note = input("Note (optional): ").strip()
        budget.save_expense(SavedExpense(name, category, amount, note))
        print(f"  Saved '{name}'.")
    elif choice == "d" and budget.saved:
        raw = input("Number to delete: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(budget.saved):
            removed = budget.saved.pop(int(raw) - 1)
            print(f"  Deleted '{removed.name}'.")


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
                add_expense(budget, month, month_key)
            elif choice == "4":
                manage_saved(budget)
            elif choice == "5":
                list_expenses(month)
            elif choice == "6":
                delete_expense(month)
            elif choice == "7":
                print(render(summarize(month), month_key))
            elif choice == "8":
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
