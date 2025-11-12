import argparse
import json
import pandas as pd
import csv
from datetime import datetime
import calendar
import os
from tabulate import tabulate


LIMITS_FILE = "budget.json"
FILENAME = "expense.csv"
FIELDS = ["ID", "Date", "Description", "Amount", "Category"]
CATEGORIES = [
    "Housing",
    "Food",
    "Transport",
    "Healthcare",
    "Utilities",
    "test",
]


def positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(f"Value must be >= 1, received {value}")
    return ivalue


def get_id(data):
    # if data is empty. first row are fields.
    if len(data) == 1:
        return 1

    used_id = []
    for expense in data[1:]:
        if expense[0].isdigit():
            used_id.append(int(expense[0]))
        else:
            print("Found non digit ID. Please check it out!")

    used_id.sort()

    if used_id[0] == 2:
        return 1

    for i in range(len(used_id)):
        try:
            if used_id[i] + 1 != used_id[i + 1]:
                result = used_id[i] + 1
                break
        except IndexError:
            result = used_id[i] + 1

    return result


def get_month_boundaries(month_number: int, year: int = None):
    if year is None:
        year = datetime.now().year

    try:
        target_date = datetime(year, month_number, 1)
    except ValueError:
        raise ValueError("Invalid month number. Use numbers from 1 to 12.")

    start_of_month = target_date
    _, num_days_in_month = calendar.monthrange(year, month_number)
    end_of_month = target_date.replace(day=num_days_in_month)
    date_format = "%Y-%m-%d"

    start_date_str = start_of_month.strftime(date_format)
    end_date_str = end_of_month.strftime(date_format)

    return start_date_str, end_date_str


def get_month_name(month):
    month_map = {
        "1": "January",
        "01": "January",
        "january": "January",
        "2": "February",
        "02": "February",
        "february": "February",
        "3": "March",
        "03": "March",
        "march": "March",
        "4": "April",
        "04": "April",
        "april": "April",
        "5": "May",
        "05": "May",
        "may": "May",
        "6": "June",
        "06": "June",
        "june": "June",
        "7": "July",
        "07": "July",
        "july": "July",
        "8": "August",
        "08": "August",
        "august": "August",
        "9": "September",
        "09": "September",
        "september": "September",
        "10": "October",
        "october": "October",
        "11": "November",
        "november": "November",
        "12": "December",
        "december": "December",
    }
    key = str(month).strip().lower()
    if key in month_map:
        return month_map[key]
    else:
        raise ValueError("Invalid month input")


def get_month_number(month):
    month = month.capitalize()
    months = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12",
    }

    if isinstance(month, str):
        month = month.strip()

    if month.isdigit():
        month_number = int(month)
        if 1 <= month_number <= 12:
            return f"{month_number:02d}"
        else:
            raise ValueError("The month number must be beetwen 1 and 12")

    elif month in months:
        return months[month]

    else:
        raise ValueError("Incorrect month entry")


def write_data(filename: str, data: list):
    with open(filename, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)
    print("File is rewritten.")


def load_data(filename: str):
    data = []
    if os.path.exists(filename) and os.path.getsize(filename) != 0:
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                data.append(row)
    else:
        with open(filename, "w", encoding="utf-8") as file:
            pass
        data = [FIELDS]

    return data


def update_description(filename, ID, description):
    x = list(load_data(filename))
    for task in x:
        if task[0] == ID:
            task[2] = description
    write_data(filename, x)
    print("Description updated successfully")


def update_amount(filename, ID, amount):
    x = list(load_data(filename))
    for task in x:
        if task[0] == ID:
            task[3] = amount
    write_data(filename, x)
    print("Amount updated successfully")


# i dont want to use any external libraries but have no choices to implement this.
def list_expenses(args):
    df = pd.read_csv(FILENAME)
    filtered_df = df

    if args.category:
        filtered_df = filtered_df[filtered_df["Category"] == args.category]

    if args.month:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == args.month]

    print(tabulate(filtered_df, headers="keys", tablefmt="github"))


def get_summary(data, month=None):
    summary = 0
    if month:
        for expense in data[1:]:
            datetime_obj = datetime.strptime(expense[1], "%Y-%m-%d")
            if datetime_obj.month == month:
                summary += float(expense[3])
    else:
        for expense in data[1:]:
            summary += float(expense[3])
    return summary


# checks if id exists for delete argument
def id_exists(data, id_to_delete):
    target = str(id_to_delete).strip()
    for row in data[1:]:
        if row and str(row[0]).strip() == target:
            return True
    return False

def get_limit(limit_file, month):
    try:
        with open(limit_file, "r") as lmtfile:
            lmtfile.seek(0)
            content = lmtfile.read().strip()

            if not content:
                return []

            data = json.load(lmtfile)

            for limit in data:
                if limit["name"] == month:
                    return limit

            return []

    except Exception as e:
        print(e, "Error")

def limit_exists(limit_file, month):
    try:
        with open(limit_file, "r") as lmtfile:
            lmtfile.seek(0)
            content = lmtfile.read().strip()

            # if file is empty return False
            if not content:
                return False

            lmtfile.seek(0)
            data = json.load(lmtfile)
            for limit in data:
                if limit.get("name") == month:
                    print(
                        f"""
    There's already a budget for this month
    Month: {limit["name"]}
    Budget: {limit["amount"]}
    Spent this month: {limit["spentSoFar"]}
                """
                    )
                    return True

        return False

    except FileNotFoundError:
        with open(limit_file, "w", encoding="utf-8") as lmtfile:
            json.dump([], lmtfile, indent=4)
            return False

    except json.JSONDecodeError:
        print(f"Error: Json file '{limit_file}' is corrupted. Reinitializing.")
        with open(limit_file, "w", encoding="utf-8") as lmtfile:
            json.dump([], lmtfile, indent=4)
        return False


def add_limit(limit_file_name, new_budget):
    try:
        with open(limit_file_name, "r", encoding="utf-8") as lmtfile:
            content = lmtfile.read()
            if content:
                json_data = json.loads(content)
            else:
                json_data = []
    except FileNotFoundError:
        print(f"File {limit_file_name} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file.")

    json_data.append(new_budget)

    with open(limit_file_name, "w", encoding="utf-8") as lmtfile:
        json.dump(json_data, lmtfile, indent=4, ensure_ascii=False)

    print(
        f"""
    New budget has been added.
    Month: {new_budget["name"]}
    Amount: {new_budget["amount"]}
    """
    )


def get_current_limit_data(limit_file_name, month):
    try:
        with open(limit_file_name, "r", encoding="utf-8") as lmtfile:
            content = lmtfile.read()
            if content:
                json_data = json.loads(content)
            else:
                return None

    except FileNotFoundError:
        print(f"No budget has been assigned at this time")
        return None
    except json.JSONDecoreError:
        print(f"Json error happened.")
        return None

    for limit in json_data:
        if limit.get("month") == month:
            return limit


def check_budget(limit_file_name):
    def decorator(func):
        def wrapper(filename, data, expense):
            date_obj = datetime.strptime(expense[1], "%Y-%m-%d")
            month_expense = get_month_name(date_obj.month)

            # START LOGIC

            if limit_exists(limit_file_name, month_expense):
                limit = get_limit(limit_file_name, month_expense)

            month_budget = limit["amount"]

            month_sum = get_summary(month_expense)

            if month_sum < month_budget:
                print("LESS")
                


        return wrapper

    return decorator


def delete_expense(data, ID):
    for expense in data[1:]:
        if expense[0] == ID:
            data.remove(expense)
    write_data(FILENAME, data)
    print(f"Expense deleted successfully.")

@check_budget(LIMITS_FILE)
def add_data(filename: str, data: list, expense: list):
    data.append(expense)
    with open(filename, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)
    print(f"Expense added successfully. (ID : {expense[0]}) ")


def main():
    # --- CREATE PARSER ---
    parser = argparse.ArgumentParser(
        description="Expense tracker CLI application.",
        epilog="""
-------- QUICK START EXAMPLES --------

1. Adding a new expense:
   $ python main.py add --amount 500 --category Food --description Coffee break

2. Setting a monthly budget limit:
   $ python main.py set-limit --month 11 --amount 30000

3. Viewing the overall summary for the current month:
   $ python main.py summary --month 10

4. Updating an existing expense (assuming expense ID is 5):
   $ python main.py update --id 5 --amount 550

---
For detailed information on the arguments for a specific command, use:
$ python main.py <command> -h
(Example: python main.py list -h)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- ADD ---
    add_parser = subparsers.add_parser(
        "add",
        help="Add an expense",
        description="Command allow you to add new expense",
        epilog="""
            Example:
                main.py add -d New mouse for work -a 1500 -c Utilities
                main.py add -d Lunch -a 250 -c Food
                """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_parser.add_argument(
        "-d",
        "--description",
        nargs="+",
        required=True,
        help="Brief description of consumption",
    )
    add_parser.add_argument(
        "-a",
        "--amount",
        type=positive_int,
        required=True,
        help="Amount of expenses in currency $$$",
    )
    add_parser.add_argument(
        "-c",
        "--category",
        choices=CATEGORIES,
        required=True,
        help=("Allowed categories: " + ", ".join(CATEGORIES)),
        metavar="",
    )

    # --- UPDATE ---
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing expense",
        description="Command allows you to update description or amount of an existing expense by id.",
        epilog="""
            Example:
                main.py update --id 1 --description <new desc>
                main.py update --id 1 --amount <new integer amount>
                main.py update --id 125 -d <new desc> -a <new integer amount>
                """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    update_parser.add_argument("--id", type=positive_int, help="Expense ID")

    update_parser.add_argument(
        "-d", "--description", nargs="+", help="Update descripion"
    )
    update_parser.add_argument("-a", "--amount", help="Update amount")

    # --- LIST ---
    list_parser = subparsers.add_parser(
        "list",
        help="List all expenses",
        description="Command allow you to list all expenses or a specific one",
        epilog="""
            Example:
                main.py list
                main.py list -m 10
                main.py list --category Housing
                main.py list --month 10 -c Housing
                """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    list_parser.add_argument(
        "-m",
        "--month",
        type=int,
        choices=range(1, 13),
        help="List a certain month (1-12)",
        metavar="",
    )

    list_parser.add_argument(
        "-c",
        "--category",
        choices=CATEGORIES,
        help=("Alowed categories: " + ", ".join(CATEGORIES)),
        metavar="",
    )

    # --- SUMMARY ---
    summary_parser = subparsers.add_parser(
        "summary",
        help="Summary expenses",
        description="Command allows you to summarize all expenses or for a specific month",
        epilog="""
            Example:
                main.py summary
                main.py summary -m 10
                main.py summary --month 10
                   """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    summary_parser.add_argument(
        "-m",
        "--month",
        type=int,
        choices=range(1, 13),
        help="To summary in a certain month",
        metavar="MONTH",
    )

    # --- DELETE ---
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an expense",
        description="Command allows you to delete an expense by id",
        epilog="""
            Example:
                main.py delete --id 1
                """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    delete_parser.add_argument("--id", type=positive_int, help="Expense ID to delete")

    # --- SET LIMIT ---
    limit_parser = subparsers.add_parser(
        "set-limit",
        help="Set a budget for a certain month",
        description="Command allows you to set a budget limit for one month.",
        epilog="""
        Examples:
            main.py set-limit -m 3 -l 15000
            main.py set-limit --month 7 --limit 120
            """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    limit_parser.add_argument(
        "-l", "--limit", type=positive_int, help="Budget limit amount", metavar="AMOUNT"
    )

    limit_parser.add_argument(
        "-m",
        "--month",
        type=int,
        choices=range(1, 13),
        metavar="MONTH",
        help="Set a budget for the month. (1-12)",
    )

    # --- PARSE ARGUMENTS ---
    args = parser.parse_args()

    # --- LOAD DATA ---
    data = load_data(FILENAME)

    match args.command:
        case "add":
            add_data(
                FILENAME,
                data,
                [
                    get_id(data),
                    datetime.now().strftime("%Y-%m-%d"),
                    " ".join(args.description),
                    args.amount,
                    args.category,
                ],
            )

        case "update":
            if args.description:
                update_description(FILENAME, args.id, " ".join(args.description))

            if args.amount:
                update_amount(FILENAME, args.id, args.amount)

        case "list":
            list_expenses(args)

        case "summary":
            if args.month:
                print(
                    f"Total expenses for {get_month_name(args.month)}: ${get_summary(data=data, month=get_month_number(args.month))}"
                )
            else:
                print(f"Total expenses: ${get_summary(data)}")

        case "delete":
            if args.id:
                if id_exists(data, args.id):
                    delete_expense(data, args.id)
            else:
                print("Enter the ID using --id <expense id>")

        case "set-limit":
            start, end = get_month_boundaries(month_number=args.month)
            new_entry = {
                "name": get_month_name(args.month),
                "amount": args.limit,
                "periodStart": start,
                "periodEnd": end,
                "spentSoFar": get_summary(data=data, month=args.month),
            }


if __name__ == "__main__":
    main()
    # limit_exists(LIMITS_FILE, get_month_name(11))
