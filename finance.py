"""
finance.py

A financial tracking module that supports categorizing expenses, analyzing transactions,
and summarizing financial data using NLP techniques.
"""

import os
import datetime
import json
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
from tabulate import tabulate
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


class Category:
    """Handles expense categorization, including auto-categorization using keywords."""

    CATEGORIES = [
        "Groceries",
        "Rent",
        "Utilities",
        "Entertainment",
        "Transportation",
        "Shopping",
        "Health",
        "Other",
    ]

    @classmethod
    def list_categories(cls):
        """Return list of available expense categories."""
        return cls.CATEGORIES

    @staticmethod
    def auto_categorize(description: str) -> str:
        """Automatically categorize expense based on description keywords."""

        description = description.lower()
        keywords = {
            "food": "Groceries",
            "supermarket": "Groceries",
            "rent": "Rent",
            "electricity": "Utilities",
            "water": "Utilities",
            "movie": "Entertainment",
            "cinema": "Entertainment",
            "bus": "Transportation",
            "car": "Transportation",
            "fuel": "Transportation",
            "uber": "Transportation",
            "clothes": "Shopping",
            "shopping": "Shopping",
            "hospital": "Health",
            "medication": "Health",
            "trip": "Entertainment",
            "shoes": "Shopping",
            "drugs": "Health",
        }

        lemmatizer = WordNetLemmatizer()
        words = word_tokenize(description)

        for word in words:
            lemma = lemmatizer.lemmatize(word)
            if lemma in keywords:
                return keywords[lemma]

        # Try finding a similar word in WordNet
        for word in words:
            lemma = lemmatizer.lemmatize(word)
            synsets = wordnet.synsets(lemma)
            for synset in synsets:
                for lemma_name in synset.lemma_names():
                    if lemma_name in keywords:
                        return keywords[lemma_name]

        return "Other"


@dataclass
class Transaction:
    """Represents a financial transaction with date, amount, category, and description."""

    date: datetime.date
    amount: float
    category: str
    description: str
    transaction_type: str

    def to_dict(self):
        """Convert transaction to dictionary format."""

        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "transaction_type": self.transaction_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create transaction from dictionary data."""

        return cls(
            date=datetime.date.fromisoformat(data["date"]),
            amount=float(data["amount"]),
            category=data["category"],
            description=data["description"],
            transaction_type=data["transaction_type"],
        )


class FinanceTracker:
    """Main class for tracking financial transactions, budgets, and generating reports."""

    def __init__(self, username: str):
        self.username = username
        self.transactions: Dict[str, List[Transaction]] = {"income": [], "expense": []}
        self.budgets: Dict[str, float] = {}
        # ✅ Ensure the transactions folder exists
        transactions_dir = Path("transactions")
        transactions_dir.mkdir(exist_ok=True)  # Creates folder if it doesn't exist

        # ✅ Set up the transaction file path
        self.transactions_file = transactions_dir / f"{username}_transactions.json"

        self.load_transactions()

    def get_balance(self):
        """Calculate current balance (total income - total expenses)."""
        total_income = sum(t.amount for t in self.transactions["income"])
        total_expense = sum(t.amount for t in self.transactions["expense"])
        return total_income - total_expense

    def load_transactions(self):
        """Load transactions and budgets from JSON file."""
        if self.transactions_file.exists():
            with open(self.transactions_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                transactions_data = data.get("transactions", {})

                if isinstance(transactions_data, dict):
                    self.transactions = {
                        "income": [
                            Transaction.from_dict(t)
                            for t in transactions_data.get("income", [])
                        ],
                        "expense": [
                            Transaction.from_dict(t)
                            for t in transactions_data.get("expense", [])
                        ],
                    }
                else:
                    self.transactions = {"income": [], "expense": []}
                    print("Warning: Invalid transactions format. Resetting to default.")

                self.budgets = data.get("budgets", {})

                if not isinstance(self.budgets, dict):
                    self.budgets = {}
                    print("Warning: Invalid budgets format. Resetting to default.")
        else:
            self.save_transactions()

    def save_transactions(self):
        """Save transactions and budgets to JSON file."""
        data = {
            "transactions": {
                "income": [t.to_dict() for t in self.transactions["income"]],
                "expense": [t.to_dict() for t in self.transactions["expense"]],
            },
            "budgets": self.budgets,
        }
        with open(self.transactions_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def add_transaction(self):
        """Add a new income or expense transaction."""

        try:
            print(f"\nAdding a new transaction for {self.username}...")
            transaction_type = input("Enter type (income/expense): ").lower()
            if transaction_type not in ["income", "expense"]:
                raise ValueError(
                    "Invalid transaction type. Choose 'income' or 'expense'."
                )

            date_str = input(
                "Enter the date (YYYY-MM-DD) or press enter to ue today's date: "
            )
            if not date_str:
                date = datetime.date.today()
            else:
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date > datetime.date.today():
                        print(
                            "Warning: You are adding a transaction with a future date!"
                        )
                except ValueError:
                    print("Invalid date format: please YYYY-MM-DD")
                    return

            amount = float(input("Enter amount: "))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            if transaction_type == "expense" and amount > self.get_balance():
                print("\n⚠️ Warning: Insufficient balance! Transaction not added.\n")
                return

            description = input("Enter description: ")
            category = (
                Category.auto_categorize(description)
                if transaction_type == "expense"
                else "Salary"
            )

            new_transaction = Transaction(
                date, amount, category, description, transaction_type
            )
            if new_transaction in self.transactions[transaction_type]:
                print("Transaction already exists! \n")
                return

            self.transactions[transaction_type].append(new_transaction)
            self.save_transactions()

            # Real-time budget alert
            if transaction_type == "expense" and category in self.budgets:
                spent = sum(
                    t.amount
                    for t in self.transactions["expense"]
                    if t.category == category
                )
                if spent > self.budgets[category]:
                    print(
                        f"\n⚠️ Warning: You have exceeded your budget for {category}!\n"
                    )

            print("\nTransaction added successfully!\n")

            balance = self.get_balance()
            if balance < 100:
                print(f"⚠️ Warning: Your balance is low! Remaining: ${balance}")

        except (ValueError, KeyError, FileNotFoundError) as e:
            print(f"\nAn error occurred: {e}\n")

    def delete_transaction(self):
        """Delete selected transactions by index."""

        print("\nDelete Transactions\n")
        all_transactions = self.transactions["income"] + self.transactions["expense"]

        if not all_transactions:
            print("No transactions recorded.\n")
            return

        headers = ["Index", "Date", "Amount", "Category", "Description", "Type"]
        rows = [
            [i, t.date, t.amount, t.category, t.description, t.transaction_type]
            for i, t in enumerate(all_transactions)
        ]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        try:
            indices = input("Enter transaction indices to delete (comma-separated): ")
            indices = sorted(set(map(int, indices.split(","))), reverse=True)

            if all(0 <= index < len(all_transactions) for index in indices):
                for index in indices:
                    transaction = all_transactions.pop(index)
                    self.transactions[transaction.transaction_type].remove(transaction)

                self.save_transactions()
                print("Selected transactions deleted successfully!\n")
            else:
                print("Invalid indices. Please enter valid numbers from the list.\n")

        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.\n")

    def update_transaction(self):
        """Update an existing transaction."""
        print("\nUpdate a Transaction\n")
        all_transactions = self.transactions["income"] + self.transactions["expense"]
        if not all_transactions:
            print("No transactions recorded.\n")
            return

        headers = ["Index", "Date", "Amount", "Category", "Description", "Type"]
        rows = [
            [i, t.date, t.amount, t.category, t.description, t.transaction_type]
            for i, t in enumerate(all_transactions)
        ]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        try:
            index = int(input("Enter transaction index to update: "))
            if 0 <= index < len(all_transactions):
                transaction = all_transactions[index]

                new_date = (
                    input(f"Enter new date (YYYY-MM-DD) [{transaction.date}]: ")
                    or transaction.date
                )
                new_amount = input(f"Enter new amount [{transaction.amount}]: ")
                new_category = (
                    input(f"Enter new category [{transaction.category}]: ")
                    or transaction.category
                )
                new_description = (
                    input(f"Enter new description [{transaction.description}]: ")
                    or transaction.description
                )
                new_type = (
                    input(
                        f"Enter new type (income/expense) [{transaction.transaction_type}]: "
                    )
                    or transaction.transaction_type
                )

                transaction.date = (
                    datetime.date.fromisoformat(str(new_date))
                    if isinstance(new_date, str) and new_date.strip()
                    else transaction.date
                )

                transaction.amount = (
                    float(new_amount) if new_amount else transaction.amount
                )
                transaction.category = new_category
                transaction.description = new_description
                transaction.transaction_type = new_type

                self.save_transactions()
                print("Transaction updated successfully!\n")
            else:
                print("Invalid index.\n")
        except ValueError:
            print("Invalid input. Please enter the correct values.\n")

    def view_transactions(self):
        """Display all transactions in a table format."""

        all_transactions = self.transactions["income"] + self.transactions["expense"]
        if not all_transactions:
            print("\nNo transactions recorded.\n")
            return
        print("\nAll Transactions\n")
        headers = ["Date", "Amount", "Category", "Description", "Type"]
        rows = [
            [t.date, t.amount, t.category, t.description, t.transaction_type]
            for t in all_transactions
        ]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print()

    def import_transactions(self, file_path):
        """Import transactions from CSV or JSON file."""

        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".json"):
                df = pd.read_json(file_path)
            else:
                print("Invalid file format. Please provide a CSV or JSON file.")
                return

            df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.strftime(
                "%Y-%m-%d"
            )

            added_count = 0
            duplicate_count = 0

            for _, row in df.iterrows():
                transaction = Transaction(
                    date=datetime.date.fromisoformat(row["date"]),
                    amount=float(row["amount"]),
                    category=row["category"],
                    description=row["description"],
                    transaction_type=row["transaction_type"],
                )

                if transaction in self.transactions[transaction.transaction_type]:
                    duplicate_count += 1
                    continue

                self.transactions[transaction.transaction_type].append(transaction)
                added_count += 1

            self.save_transactions()
            print(f"\n {added_count} new transactions imported successfully!")
            print(f"{duplicate_count} duplicate transactions skipped. \n")

        except (ValueError, KeyError, FileNotFoundError) as e:
            print(f"\nError importing transactions: {e}\n")

    def view_financial_summary(self):
        """Display comprehensive financial summary with income, expenses, and budgets."""

        print("\nFinancial Summary\n")

        # Display all income transactions
        print("Income Breakdown:")
        income_headers = ["Date", "Amount", "Description"]
        income_rows = [
            [t.date, t.amount, t.description] for t in self.transactions["income"]
        ]
        print(tabulate(income_rows, headers=income_headers, tablefmt="fancy_grid"))

        total_income = sum(t.amount for t in self.transactions["income"])
        print(f"Total Income: {total_income}\n")

        # Display all expense transactions
        print("Expense Breakdown:")
        expense_headers = ["Date", "Amount", "Category", "Description"]
        expense_rows = [
            [t.date, t.amount, t.category, t.description]
            for t in self.transactions["expense"]
        ]
        print(tabulate(expense_rows, headers=expense_headers, tablefmt="fancy_grid"))

        total_expense = sum(t.amount for t in self.transactions["expense"])
        net_savings = total_income - total_expense
        print(f"Total Expenses: {total_expense}")
        print(f"Actual Savings (after expenses): {net_savings}\n")

        # Display budget breakdown
        print("Budget Breakdown:")
        budget_headers = ["Category", "Budgeted Amount", "Spent", "Remaining"]
        budget_rows = []
        total_budget = sum(self.budgets.values())
        for category, budget in self.budgets.items():
            spent = sum(
                t.amount for t in self.transactions["expense"] if t.category == category
            )
            remaining = budget - spent
            budget_rows.append([category, budget, spent, remaining])
        print(tabulate(budget_rows, headers=budget_headers, tablefmt="fancy_grid"))

        planned_savings = total_income - total_budget
        print(f"Total Budget Allocation: {total_budget}")
        print(f"Planned Savings (after budgeting): {planned_savings}\n")


    def search_transactions(self):
        """Search transactions by keyword in date, category, or description."""

        print("\nSearch Transactions\n")
        keyword = input("Enter keyword (date, category, or description): ").lower()
        filtered = [
            t
            for t in self.transactions["income"] + self.transactions["expense"]
            if keyword in t.date.strftime("%Y-%m-%d")
            or keyword in t.category.lower()
            or keyword in t.description.lower()
        ]
        if not filtered:
            print("\nNo matching transactions found.\n")
            return
        headers = ["Date", "Amount", "Category", "Description", "Type"]
        rows = [
            [t.date, t.amount, t.category, t.description, t.transaction_type]
            for t in filtered
        ]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print()

    def export_financial_summary(self):
        """Export financial summary to CSV or JSON format."""

        folder_name = "financial_summary"
        os.makedirs(folder_name, exist_ok=True)

        # Display menu for file format selection
        print("\nChoose export format:")
        print("1. CSV")
        print("2. JSON")

        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == "1":
                file_format = "csv"
                break
            if choice == "2":
                file_format = "json"
                break
            print("Invalid choice. Please enter 1 or 2.")

        # Define file path
        file_name = f"financial_report.{file_format}"
        file_path = os.path.join(folder_name, file_name)

        try:
            # Process income data
            income_data = [
                [t.date.isoformat(), t.amount, t.description]
                for t in self.transactions["income"]
            ]
            income_sum = sum(t.amount for t in self.transactions["income"])

            # Process expense data
            expense_data = [
                [t.date.isoformat(), t.amount, t.category, t.description]
                for t in self.transactions["expense"]
            ]
            total_expense = sum(t.amount for t in self.transactions["expense"])
            net_savings = income_sum - total_expense

            # Process budget data
            budget_data = []
            for category, budget in self.budgets.items():
                spent = sum(
                    t.amount
                    for t in self.transactions["expense"]
                    if t.category == category
                )
                remaining = budget - spent
                budget_data.append([category, budget, spent, remaining])

            total_budget = sum(self.budgets.values())
            planned_savings = income_sum - total_budget

            # Export as CSV
            if file_format == "csv":
                with open(file_path, "w", newline="", encoding="utf-8") as file:
                    file.write("Income Breakdown\n")
                    df_income = pd.DataFrame(
                        income_data, columns=["Date", "Amount", "Description"]
                    )
                    if not df_income.empty:
                        df_income.to_csv(file, index=False, mode="a")
                    file.write(f"\nTotal Income: {income_sum} \n\n")

                    file.write("Expense Breakdown\n")
                    df_expense = pd.DataFrame(
                        expense_data,
                        columns=["Date", "Amount", "Category", "Description"],
                    )
                    if not df_expense.empty:
                        df_expense.to_csv(file, index=False, mode="a")
                    file.write(f"\nTotal Expenses: {total_expense} \n")
                    file.write(f"Actual Savings (after expenses): {net_savings} \n\n")

                    file.write("Budgets Breakdown\n")
                    df_budget = pd.DataFrame(
                        budget_data,
                        columns=["Category", "Budgeted Amount", "Spent", "Remaining"],
                    )
                    if not df_budget.empty:
                        df_budget.to_csv(file, index=False, mode="a")

                    file.write(f"\nTotal Budget Allocation: {total_budget} \n")
                    file.write(
                        f"Planned Savings (after budgeting): {planned_savings} \n"
                    )

            # Export as JSON
            elif file_format == "json":
                data = {
                    "income": {"transactions": income_data, "total_income": income_sum},
                    "expense": {
                        "breakdown": expense_data,
                        "total_expense": total_expense,
                        "net_savings": net_savings,
                    },
                    "budgets": {
                        "transactions": budget_data,
                        "total_budget": total_budget,
                        "planned_savings": planned_savings,
                    },
                }
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

            print(f"\nFinancial summary successfully exported to {file_path}\n")

        except (ValueError, KeyError, FileNotFoundError) as e:
            print(f"\nAn error occurred: {e}\n")

    def set_budget(self):
        """Set budget amount for a specific category."""

        print("\nSet Budget for a Category\n")
        print("Available Categories:")
        for i, cat in enumerate(Category.list_categories(), 1):
            print(f"{i}. {cat}")
        try:
            cat_choice = int(input("Select category number: "))
            category = Category.list_categories()[cat_choice - 1]
            amount = float(input("Enter budget amount: "))
            if amount <= 0:
                raise ValueError("Budget amount must be greater than zero.")

            total_income = sum(t.amount for t in self.transactions["income"])
            total_budget = sum(self.budgets.values()) + amount

            if total_budget > total_income:
                print(
                    f"\nError: Total budget allocation ({total_budget}) "
                    f"exceeds total income ({total_income}). Please adjust the budget.\n"
                )
                return

            self.budgets[category] = amount
            self.save_transactions()
            print(f"\nBudget set for {category}: {amount}\n")
        except (ValueError, KeyError, FileNotFoundError) as e:
            print(f"\nAn error occurred: {e}\n")

    def view_budget(self):
        """Display budget overview with spent amounts and remaining balances."""

        print("\nBudget Overview\n")
        if not self.budgets:
            print("No budgets set.\n")
            return
        headers = ["Category", "Budget", "Spent", "Remaining"]
        rows = []
        for category, budget in self.budgets.items():
            spent = sum(
                t.amount for t in self.transactions["expense"] if t.category == category
            )
            remaining = budget - spent
            rows.append([category, budget, spent, remaining])
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print()

    def spending_reports_by_category(self):
        """Generate spending reports grouped by category."""

        print("\nSpending Reports by Category\n")
        if not self.transactions["expense"]:
            print("No expense transactions recorded.\n")
            return

        category_totals = {}
        for transaction in self.transactions["expense"]:
            category_totals[transaction.category] = (
                category_totals.get(transaction.category, 0) + transaction.amount
            )

        headers = ["Category", "Total Spent"]
        rows = [[category, amount] for category, amount in category_totals.items()]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        # Identify Top 3 Spending Categories
        sorted_categories = sorted(
            category_totals.items(), key=lambda x: x[1], reverse=True
        )
        print("\nTop 3 Spending Categories:")
        for i, (category, amount) in enumerate(sorted_categories[:3], 1):
            print(f"{i}. {category}: {amount}")

        # Identify Biggest Expense
        biggest_expense = max(
            self.transactions["expense"], key=lambda t: t.amount, default=None
        )
        if biggest_expense:
            print("\nBiggest Expense:")
            print(
                f"{biggest_expense.category} - {biggest_expense.amount}"
                f"on {biggest_expense.date} ({biggest_expense.description})"
            )
        print()
