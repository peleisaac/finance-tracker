"""
Command-line interface module for Finance Tracker Application.

This module provides CLI functionality for the finance tracker, allowing users
to perform various operations like adding transactions, importing/exporting data
through command-line arguments.
"""

import datetime
import argparse
import getpass
import sys
from finance import Transaction, FinanceTracker
from auth import UserAuthentication  # Import authentication module


def parse_args():
    """
    Parse command-line arguments for the Finance Tracker CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments with username validation
    """
    parser = argparse.ArgumentParser(description="Finance Tracker CLI")

    # Username argument (now optional in argparse but required in logic)
    parser.add_argument(
        "--username", type=str, help="Specify username (Required for all actions)"
    )

    # Transaction options
    parser.add_argument("--add-income", type=float, help="Add an income transaction")
    parser.add_argument("--add-expense", type=float, help="Add an expense transaction")
    parser.add_argument("--category", type=str, help="Specify transaction category")
    parser.add_argument("--description", type=str, help="Transaction description")
    parser.add_argument(
        "--date", type=str, help="Specify transaction date (YYYY-MM-DD)"
    )

    # File operations
    parser.add_argument(
        "--export", type=str, help="Export financial summary (CSV/JSON)"
    )
    parser.add_argument("--inport", type=str, help="Import transactions from CSV/JSON")

    parsed_args = parser.parse_args()

    # If username is not provided, ask for it interactively
    if not parsed_args.username:
        parsed_args.username = input("Enter your username: ").strip()
        if not parsed_args.username:
            print("❌ Error: Username is required.")
            sys.exit(1)  # Exit the script

    return parsed_args


def handle_args(parsed_args):
    """
    Handle command-line arguments and ensure the user exists before performing actions.
    
    Args:
        parsed_args (argparse.Namespace): Parsed command-line arguments
    """
    auth = UserAuthentication()  # Create an authentication instance

    # Validate username before proceeding
    if not auth.check_user_exists(parsed_args.username):
        print(
            f"\n❌ Error: No account found for '{parsed_args.username}'."
            f"Please register or try again.\n"
        )
        return

    # Optional: Require password for extra security
    password = getpass.getpass(f"🔒 Enter password for {parsed_args.username}: ")
    if not auth.verify_login(parsed_args.username, password):
        print("\n❌ Incorrect password. Access denied.\n")
        return

    # Initialize FinanceTracker with verified user
    tracker = FinanceTracker(parsed_args.username)

    if parsed_args.add_income or parsed_args.add_expense:
        transaction_type = "income" if parsed_args.add_income else "expense"
        amount = parsed_args.add_income if parsed_args.add_income else parsed_args.add_expense
        category = parsed_args.category if parsed_args.category else "Other"
        description = parsed_args.description if parsed_args.description else "No description"
        date = (
            datetime.date.today()
            if not parsed_args.date
            else datetime.datetime.strptime(parsed_args.date, "%Y-%m-%d").date()
        )

        # Create transaction object
        transaction = Transaction(date, amount, category, description, transaction_type)

        # Check if the transaction already exists before adding
        if transaction in tracker.transactions[transaction.transaction_type]:
            print("\n⚠️ Duplicate transaction detected! Entry not added.\n")
            return

        # If unique, add transaction
        tracker.transactions[transaction.transaction_type].append(transaction)
        tracker.save_transactions()
        print(f"\n✅ {transaction_type.capitalize()} of {amount} added successfully!\n")

    if parsed_args.export:
        tracker.export_financial_summary()
        print(f"\n✅ Financial summary exported to {parsed_args.export}!\n")

    if parsed_args.inport:
        tracker.import_transactions(parsed_args.inport)
        print(f"\n✅ Transactions imported from {parsed_args.inport}!\n")


if __name__ == "__main__":
    cli_args = parse_args()
    handle_args(cli_args)
