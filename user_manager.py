"""
User Manager for To-Do List Application
Handles user authentication and registration
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List  # Added List import here

class UserManager:
    """Manages user authentication and registration"""
    
    def __init__(self, users_file="data/users.json"):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, create new one
                return {}
        return {}
    
    def save_users(self) -> bool:
        """Save users to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        # Add a pepper (secret string) for extra security
        pepper = "todo_app_secret_pepper_2024"
        salted_password = password + pepper
        
        return hashlib.sha256(salted_password.encode()).hexdigest()
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate username"""
        username = username.strip()
        
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 20:
            return False, "Username cannot exceed 20 characters"
        
        # Check for valid characters (alphanumeric and underscores)
        if not username.isalnum() and '_' not in username:
            return False, "Username can only contain letters, numbers, and underscores"
        
        # Check if username already exists
        if username in self.users:
            return False, "Username already exists"
        
        return True, "Username is valid"
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if len(password) > 50:
            return False, "Password is too long (max 50 characters)"
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one number"
        
        # Check for at least one letter
        if not any(char.isalpha() for char in password):
            return False, "Password must contain at least one letter"
        
        return True, "Password is valid"
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Register a new user"""
        try:
            # Validate username
            is_valid, message = self.validate_username(username)
            if not is_valid:
                return False, message
            
            # Validate password
            is_valid, message = self.validate_password(password)
            if not is_valid:
                return False, message
            
            # Create user record
            self.users[username] = {
                'password_hash': self.hash_password(password),
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'task_count': 0,
                'completed_tasks': 0
            }
            
            # Save users
            if self.save_users():
                return True, f"User '{username}' registered successfully!"
            else:
                # Remove user if save failed
                if username in self.users:
                    del self.users[username]
                return False, "Failed to save user data"
        
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user"""
        try:
            username = username.strip()
            
            if not username:
                return False, "Please enter username"
            
            if not password:
                return False, "Please enter password"
            
            # Check if user exists
            if username not in self.users:
                return False, "User not found"
            
            # Verify password
            stored_hash = self.users[username]['password_hash']
            input_hash = self.hash_password(password)
            
            if stored_hash != input_hash:
                return False, "Incorrect password"
            
            # Update last login time
            self.users[username]['last_login'] = datetime.now().isoformat()
            self.save_users()
            
            return True, f"Welcome back, {username}!"
        
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return username in self.users
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        if username in self.users:
            return self.users[username].copy()
        return None
    
    def update_user_stats(self, username: str, stats: Dict[str, Any]) -> bool:
        """Update user statistics"""
        if username in self.users:
            for key, value in stats.items():
                if key in self.users[username]:
                    self.users[username][key] = value
            
            return self.save_users()
        return False
    
    def delete_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Delete user account"""
        try:
            # Authenticate first
            authenticated, message = self.authenticate_user(username, password)
            if not authenticated:
                return False, message
            
            # Remove user
            del self.users[username]
            
            if self.save_users():
                # Also delete user's task file
                task_file = f"data/tasks/{username}_tasks.json"
                if os.path.exists(task_file):
                    os.remove(task_file)
                
                return True, f"User '{username}' deleted successfully"
            else:
                return False, "Failed to save changes"
        
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"
    
    def get_all_users(self) -> List[str]:  # Fixed: Added List import
        """Get list of all registered users"""
        return list(self.users.keys())
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return len(self.users)