"""
Account Manager (Multi-user JSON Auth).
Manages Admin and User roles, with password authentication.
"""
import os
import json
from PyQt6.QtCore import QSettings

# Use a json file in the data directory
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")

class AccountManager:
    """Manages system users and roles using a JSON file."""

    def __init__(self):
        self.accounts = {}
        self.current_user = None
        self.current_role = None
        self._load_accounts()

    def _load_accounts(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
            
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    self.accounts = json.load(f)
            except Exception:
                self.accounts = {}
        
        # Ensure at least one admin exists
        if not any(acc.get("role") == "admin" for acc in self.accounts.values()):
            self.accounts["admin"] = {"password": "123", "role": "admin"}
            self._save_accounts()

    def _save_accounts(self):
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.accounts, f, indent=4)
        except Exception as e:
            print(f"[WARN] Failed to save accounts: {e}")

    def get_all_accounts(self):
        """Returns a list of dicts with username and role."""
        return [{"username": u, "role": d["role"]} for u, d in self.accounts.items()]

    def login(self, username: str, password: str) -> bool:
        """Verify the given password and set current session."""
        if username in self.accounts and self.accounts[username]["password"] == password:
            self.current_user = username
            self.current_role = self.accounts[username]["role"]
            return True
        return False
        
    def logout(self):
        self.current_user = None
        self.current_role = None

    def verify_password(self, password: str) -> bool:
        """Verify the current user's password."""
        if not self.current_user:
            return False
        return self.accounts[self.current_user]["password"] == password

    def change_password(self, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change the password for the currently logged in user."""
        if not self.current_user:
            return False, "Not logged in."
        if not self.verify_password(old_password):
            return False, "Incorrect old password."
        
        self.accounts[self.current_user]["password"] = new_password
        self._save_accounts()
        return True, "Password changed successfully."

    def add_account(self, username: str, password: str, role: str) -> tuple[bool, str]:
        """Add or update an account. Requires current user to be admin."""
        if self.current_role != "admin":
            return False, "Permission denied."
        if not username or not password:
            return False, "Username and password cannot be empty."
        if role not in ["admin", "user"]:
            return False, "Invalid role."
            
        self.accounts[username] = {"password": password, "role": role}
        self._save_accounts()
        return True, f"Account {username} added/updated."

    def remove_account(self, username: str) -> tuple[bool, str]:
        """Remove an account. Requires current user to be admin."""
        if self.current_role != "admin":
            return False, "Permission denied."
        if username == self.current_user:
            return False, "Cannot remove yourself."
        if username not in self.accounts:
            return False, "Account not found."
            
        # Do not allow deleting the last admin
        if self.accounts[username]["role"] == "admin":
            admin_count = sum(1 for acc in self.accounts.values() if acc.get("role") == "admin")
            if admin_count <= 1:
                return False, "Cannot delete the last admin account."
                
        del self.accounts[username]
        self._save_accounts()
        return True, f"Account {username} removed."
