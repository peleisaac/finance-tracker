"""
Main module for the personal finance tracker application.

This module provides the entry point and main menu system for managing
financial transactions, budgets, and generating reports.
"""

from finance import FinanceTracker
from menu_display import AuthMenu, Menu
from auth import UserAuthentication


class MainMenu:
    """Main menu controller for the finance tracker application."""

    def __init__(self, user_name: str):
        self.username = user_name
        self.tracker = FinanceTracker(user_name)
        self.menu = Menu(user_name)

    def get_user_balance(self):
        """Get the current user's balance."""
        return self.tracker.get_balance()

    def run(self):
        """Run the main application loop."""
        while True:
            self.menu.display_menu()
            user_choice = input("Enter your choice: ")

            if user_choice == "1":
                self.handle_transactions_menu()
            elif user_choice == "2":
                self._handle_budget_menu()
            elif user_choice == "3":
                self._handle_data_analysis_menu()
            elif user_choice == "0":
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def handle_transactions_menu(self):
        """Handle transactions submenu operations."""
        self.menu.transactions_menu()
        sub_choice = input("Enter sub-option (1-6): ")

        transaction_actions = {
            "1": self.tracker.add_transaction,
            "2": self.tracker.update_transaction,
            "3": self.tracker.delete_transaction,
            "4": self.tracker.view_transactions,
            "5": self.tracker.search_transactions,
            "6": self._handle_import_transactions,
        }

        if sub_choice in transaction_actions:
            transaction_actions[sub_choice]()
        elif sub_choice == "0":
            return
        else:
            print("Invalid choice.")

    def _handle_budget_menu(self):
        """Handle budget submenu operations."""
        self.menu.budget_menu()
        sub_choice = input("Enter sub-option (1-2): ")

        budget_actions = {
            "1": self.tracker.set_budget,
            "2": self.tracker.view_budget,
        }

        if sub_choice in budget_actions:
            budget_actions[sub_choice]()
        elif sub_choice == "0":
            return
        else:
            print("Invalid choice.")

    def _handle_data_analysis_menu(self):
        """Handle data analysis submenu operations."""
        self.menu.data_analysis_menu()
        sub_choice = input("Enter sub-option (1-3): ")

        analysis_actions = {
            "1": self.tracker.view_financial_summary,
            "2": self.tracker.export_financial_summary,
            "3": self.tracker.spending_reports_by_category,
        }

        if sub_choice in analysis_actions:
            analysis_actions[sub_choice]()
        elif sub_choice == "0":
            return
        else:
            print("Invalid choice.")

    def _handle_import_transactions(self):
        """Handle transaction import with file path input."""
        file_path = input("Enter file path for import: ")
        self.tracker.import_transactions(file_path)


def main():
    """Main entry point of the application."""
    menu = AuthMenu()
    auth = UserAuthentication()

    while True:
        menu.display_welcome_message()
        menu.auth_menu()
        auth_choice = input("Enter your choice: ")

        if auth_choice == "1":  # Register
            if auth.register():
                current_username = auth.username
                main_menu = MainMenu(current_username)
                main_menu.run()

        elif auth_choice == "2":  # Login
            if auth.login():
                current_username = auth.username
                main_menu = MainMenu(current_username)
                main_menu.run()

        elif auth_choice == "0":  # Exit
            print("Exiting application.")
            break
        else:
            print("Incorrect choice. Please pick a choice from the options in the menu")


if __name__ == "__main__":
    main()
