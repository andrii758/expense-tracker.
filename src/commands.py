import pandas as pd
import csv
from tabulate import tabulate
from datetime import datetime

from .services.expense_data import load_data, write_data
from .constants import FILENAME, LIMITS_FILE


# ВЕРНУТЬ ДЕКОРАТОР ПОСЛЕ РЕАЛИЗАЦИИ ЛИМИТОВ В budget_limit.py
# @check_budget(LIMITS_FILE)
def add_data(filename: str, data: list, expense: list):
    data.append(expense)
    with open(filename, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)
    print(f"Expense added successfully. (ID : {expense[0]}) ")


def update_description(filename, ID, description):
    x = list(load_data(filename))
    for task in x[1:]:
        if int(task[0]) == ID:
            task[2] = description
    write_data(filename, x)
    print("Description updated successfully")


def update_amount(filename, ID, amount):
    x = list(load_data(filename))
    for task in x[1:]:
        if int(task[0]) == ID:
            task[3] = amount
    write_data(filename, x)
    print("Amount updated successfully")


def delete_expense(data, ID):
    for expense in data[1:]:
        if int(expense[0]) == ID:
            data.remove(expense)
    write_data(FILENAME, data)
    print(f"Expense deleted successfully.")


# I don't want to use any external libraries but have no choices to implement this.
def list_expenses(args):
    df = pd.read_csv(FILENAME, parse_dates=["Date"])
    filtered_df = df

    if args.category:
        filtered_df = filtered_df[filtered_df["Category"] == args.category]

    if args.month:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == args.month]

    print(tabulate(filtered_df, headers="keys", tablefmt="github"))
