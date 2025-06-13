"""
User authentication module for handling registration, login, and password resets.
"""

import getpass
import re
import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import bcrypt


@dataclass
class Credentials:
    """Data structure for storing user credentials."""

    username: str
    password: str

    def to_dict(self):
        """Convert credentials to dictionary format."""
        return {
            "username": self.username,
            "password": self.password,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Credentials":
        """Create a Credentials instance from a dictionary."""
        return cls(
            username=data["username"],
            password=data["password"],
        )


class UserAuthentication:
    """Handles user registration, login, and credential management."""

    def __init__(self):
        self.credentials: Dict[str, List[Credentials]] = {"Auth": []}
        self.credentials_file = Path("credentials.json")
        self.username = None
        self.load_credentials()

    def load_credentials(self):
        """Load credentials from the JSON file."""
        if self.credentials_file.exists():
            with open(self.credentials_file, "r", encoding="utf-8") as file:
                logins = json.load(file)
                login_credentials = logins.get("credentials", {})

                if isinstance(login_credentials, dict):
                    self.credentials = {
                        "Auth": [
                            Credentials.from_dict(l)
                            for l in login_credentials.get("Auth", [])
                        ],
                    }
                else:
                    self.credentials = {"Auth": []}
                    print("Warning: Invalid credentials format.")

    def save_credentials(self):
        """Save credentials to the JSON file."""
        data = {
            "credentials": {"Auth": [l.to_dict() for l in self.credentials["Auth"]]}
        }
        with open(self.credentials_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def register(self):
        """Register a new user."""
        try:
            while True:
                username = input("Enter Username: ").lower().strip()
                if not username:
                    print("Username cannot be empty. Please enter a valid username.")
                elif any(
                    cred.username == username for cred in self.credentials["Auth"]
                ):
                    print("Username already exists. Please try a different one.")
                else:
                    break

            while True:
                password = getpass.getpass("Enter Password: ")
                if len(password) < 8:
                    print("Your password must be at least 8 characters long.")
                elif not re.search(r"\d", password):
                    print("Password must contain at least one number.")
                elif not re.search(r"[A-Z]", password):
                    print("Password must contain at least one uppercase letter.")
                elif not re.search(r"[a-z]", password):
                    print("Password must contain at least one lowercase letter.")
                else:
                    break

            hashed_password = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()
            ).decode()
            new_credentials = Credentials(username=username, password=hashed_password)
            self.credentials["Auth"].append(new_credentials)
            self.save_credentials()

            print("User registered successfully!")
            self.username = username
            return True

        except (IOError, ValueError) as e:
            print(f"Error adding credentials: {e}")
            return False

    def login(self):
        """Log in a user."""
        while True:
            username = input("Enter Username: ").lower()
            password = getpass.getpass("Enter Password: ")

            user_found = next(
                (
                    cred
                    for cred in self.credentials["Auth"]
                    if cred.username == username
                ),
                None,
            )

            if not user_found:
                print("\nNo account found for this username.")
                choice = input("Would you like to sign up? (y/n): ").strip().lower()
                if choice == "y":
                    self.register()
                else:
                    print("Returning to the main menu.")
                return False

            attempts = 3
            while attempts > 0:
                if bcrypt.checkpw(password.encode(), user_found.password.encode()):
                    print("Login Successful!")
                    self.username = username
                    return True

                attempts -= 1
                print(
                    f"\nInvalid username or password. You have {attempts} attempts remaining.\n"
                )
                if attempts > 0:
                    password = getpass.getpass("Enter Password: ")

            print("\nYou have exhausted all login attempts.")
            while True:
                choice = (
                    input("Would you like to reset your password? (y/n): ")
                    .strip()
                    .lower()
                )
                if choice == "y":
                    self.reset_password()
                    return False
                if choice == "n":
                    print("Exiting login process.")
                    return False
                print("Invalid choice. Please enter 'y' or 'n'.")

    def verify_login(self, username, password):
        """Verify if the login credentials are correct."""
        attempts = 3
        while attempts > 0:
            for cred in self.credentials["Auth"]:
                if cred.username == username:
                    if bcrypt.checkpw(password.encode(), cred.password.encode()):
                        return True
            attempts -= 1
            if attempts > 0:
                print(f"Incorrect password. You have {attempts} attempts remaining.")
                password = getpass.getpass("Re-enter Password: ")
        return False

    def check_user_exists(self, username):
        """Check if a username exists in the system."""
        return any(cred.username == username for cred in self.credentials["Auth"])

    def reset_password(self):
        """Reset a user's password."""
        username = input("Enter your username: ").lower()

        if not self.check_user_exists(username):
            print("Username not found. Please register for an account.")
            return

        user_found = next(
            (cred for cred in self.credentials["Auth"] if cred.username == username),
            None,
        )

        if not user_found:
            print("Error retrieving user data.")
            return

        while True:
            new_password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")

            if new_password != confirm_password:
                print("Passwords do not match. Try again.")
                continue
            if len(new_password) < 8:
                print("Your password must be at least 8 characters long.")
                continue
            if not re.search(r"\d", new_password):
                print("Password must contain at least one number.")
                continue
            if not re.search(r"[A-Z]", new_password):
                print("Password must contain at least one uppercase letter.")
                continue
            if not re.search(r"[a-z]", new_password):
                print("Password must contain at least one lowercase letter.")
                continue

            hashed_password = bcrypt.hashpw(
                new_password.encode(), bcrypt.gensalt()
            ).decode()
            user_found.password = hashed_password
            self.save_credentials()
            print("Password has been reset successfully!")
            return
