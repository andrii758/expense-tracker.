import argparse
from datetime import datetime

from .helpers.validation import positive_int
from .helpers.date_utils import get_month_name, get_month_boundaries

from .services.expense_data import load_data, get_id, id_exists, get_summary
from .services.budget_limit import load_limits, save_limit, check_limits
from .commands import (
    add_data,
    update_description,
    update_amount,
    delete_expense,
    list_expenses,
)
from .constants import FILENAME, CATEGORIES, LIMITS_FILE


def main():
    # --- CREATE PARSER ---
    parser = argparse.ArgumentParser(
        description="Expense tracker CLI application.",
        epilog="""
-------- QUICK START EXAMPLES --------

1. Adding a new expense:
   $ python3 -m src.main add --amount 500 --category Food --description Coffee break

2. Setting a monthly budget limit:
   $ python3 -m src.main set-limit --month 11 --amount 30000

3. Viewing the overall summary for the current month:
   $ python3 -m src.main summary --month 10

4. Updating an existing expense (assuming expense ID is 5):
   $ python3 -m src.main update --id 5 --amount 550

---
For detailed information on the arguments for a specific command, use:
$ python3 -m src.main <command> -h
(Example: python3 -m src.main list -h)
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
                python3 -m src.main add -d New mouse for work -a 1500 -c Utilities
                python3 -m src.main add -d Lunch -a 250 -c Food
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
                python3 -m src.main update --id 1 --description <new desc>
                python3 -m src.main update --id 1 --amount <new integer amount>
                python3 -m src.main update --id 125 -d <new desc> -a <new integer amount>
                """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    update_parser.add_argument("--id", type=positive_int, help="Expense ID")

    update_parser.add_argument(
        "-d", "--description", nargs="+", help="Update description"
    )
    update_parser.add_argument("-a", "--amount", help="Update amount")

    # --- LIST ---
    list_parser = subparsers.add_parser(
        "list",
        help="List all expenses",
        description="Command allows you to list all expenses or a specific one",
        epilog="""
            Example:
                python3 -m src.main list
                python3 -m src.main list -m 10
                python3 -m src.main list --category Housing
                python3 -m src.main list --month 10 -c Housing
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
        help=("Allowed categories: " + ", ".join(CATEGORIES)),
        metavar="",
    )

    # --- SUMMARY ---
    summary_parser = subparsers.add_parser(
        "summary",
        help="Summary expenses",
        description="Command allows you to summarize all expenses or for a specific month",
        epilog="""
            Example:
                python3 -m src.main summary
                python3 -m src.main summary -m 10
                python3 -m src.main summary --month 10
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
                python3 -m src.main delete --id 1
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
            python3 -m src.main set-limit -m 3 -l 15000
            python3 -m src.main set-limit --month 7 --limit 120
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
    limit_data = load_limits(LIMITS_FILE)

    match args.command:
        case "add":
            expense = [
                get_id(data),
                datetime.now().strftime("%Y-%m-%d"),
                " ".join(args.description),
                args.amount,
                args.category,
            ]
            add_data(FILENAME, data, expense)
            check_limits(limit_data, get_month_name(expense[1][5:7]), expense[3])

        case "update":
            if id_exists(data, args.id):
                if args.description:
                    update_description(FILENAME, args.id, " ".join(args.description))
                if args.amount:
                    update_amount(FILENAME, args.id, args.amount)
            else:
                print(f"ID {args.id} is not defined.")

        case "list":
            list_expenses(args)

        case "summary":
            if args.month:
                print(
                    f"Total expenses for {get_month_name(args.month)}: ${get_summary(data=data, month=args.month)}"
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
            save_limit(LIMITS_FILE, limit_data, new_entry)


if __name__ == "__main__":
    main()

