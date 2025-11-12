import os
import json
from datetime import datetime

from ..helpers.date_utils import get_month_name
from ..services.expense_data import get_summary


def load_limits(limit_filename):
    data = []
    if os.path.exists(limit_filename) and os.path.getsize(limit_filename) != 0:
        try:
            with open(limit_filename, "r", encoding="utf-8") as lmtfile:
                data = json.load(lmtfile)

        except json.JSONDecodeError:
            print(
                f"Warning: Budget file '{limit_filename} is corrupted.\nReinitializing..."
            )
            data = []
            # Rewrite the file immediately to clear the corruption
            with open(limit_filename, "w", encoding="utf-8") as lmtfile:
                json.dump(data, lmtfile)

    else:
        with open(limit_filename, "w", encoding="utf-8") as f:
            json.dump(data, f)

    return data


def save_limit(limit_filename, current_limits, new_limit):
    month_to_find = new_limit["name"]
    found = False

    for item in current_limits:
        if item["name"] == month_to_find:
            item.update(new_limit)
            found = True
            message = f"Budget for {month_to_find} has been ***updated***."
            break

    if not found:
        current_limits.append(new_limit)
        message = f"Budget for {month_to_find} has been ***added***"

    with open(limit_filename, "w", encoding="utf-8") as lmtfile:
        json.dump(current_limits, lmtfile, indent=4)

    print(message)


def check_limits(limit_data, month, amount):
    for item in limit_data:
        if item["name"] == month:
            month_limit = item["amount"]
            spent_so_far = item["spentSoFar"]
            break

    if spent_so_far + amount > month_limit:
        print(
            f"""
        Warning! Expense exceeds the monthly budget!
        Month: {month}
        Month limit: ${float(month_limit)}
        Spent so far: ${spent_so_far}
        New expense: ${float(amount)}
        ---------------------------------------------
        Over budget by: ${spent_so_far + amount - month_limit}
        """
        )
