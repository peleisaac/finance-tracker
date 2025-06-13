"""
Menu display module for Finance Tracker Application.

This module contains classes for displaying various menus in the finance tracker app,
including authentication menus and main application menus.
"""


class AuthMenu:
    """Handles authentication-related menu display."""

    def auth_menu(self):
        """Display the authentication menu with login options."""
        menu = """
        Select an option to login to the App
        
        ====================
        
        1. Register
        2. Login
        
        0. Exit
        ====================
        
        """
        print(menu)

    def display_welcome_message(self):
        """Display a welcome message for new users."""

        menu = """
        ==========================================
        Finance Tracker Application
        ==========================================
        This application helps you track 
        your finances effectively.
        
        It allows you to manage transactions, 
        track budgets, and analyze financial data.
        ==========================================
        """
        print(menu)


class Menu:
    """Handles main application menu display for logged-in users."""

    def __init__(self, username: str):
        """
        Initialize the Menu with a username.

        Args:
            username (str): The username of the logged-in user
        """
        self.username = username

    def display_menu(self):
        """Display the main application menu."""
        print(f"Finance Tracker - User: {self.username}")
        menu = """
        Welcome to your Finance Tracker Application.
        Please select an option below:
        ========================
        
        1. Manage Transactions
        2. Track Budget
        3. Financial Analysis & Reports
        
        0. Logout
        ========================
        """
        print(menu)

    def transactions_menu(self):
        """Display the transactions management menu."""
        menu = """
        Manage Transactions
        ========================
        
        1. Add Transaction
        2. Update Transaction
        3. Delete Transaction
        4. View Transactions
        5. Search Transactions
        6. Import Transactions
        
        0. Back
        ========================
        """
        print(menu)

    def budget_menu(self):
        """Display the budget tracking menu."""
        menu = """
        Track Budget
        ========================
        
        1. Set Budget
        2. View Budget
        
        0. Back
        ========================
        """
        print(menu)

    def data_analysis_menu(self):
        """Display the data analysis and reports menu."""
        menu = """
        Data Analysis & Reports
        ========================
        
        1. View Financial Summary
        2. Export Financial Summary
        3. Spending Reports by Category
        
        0. Back
        ========================
        """
        print(menu)
