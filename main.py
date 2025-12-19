import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from task_manager import TaskManager
from user_manager import UserManager
from gui import TodoAppGUI

class LoginWindow:
    """Login and Registration Window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List - Login")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window(400, 450)

        # Set application icon
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        self.user_manager = UserManager()
        self.db_manager = DatabaseManager()
        
        self.create_widgets()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
    
    def center_window(self, width, height):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create login/register widgets"""
        # Title
        title_label = ttk.Label(
            self.root, 
            text="To-Do List Application", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ttk.Label(
            self.root,
            text="Manage your tasks efficiently",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Notebook for Login/Register tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Login tab
        login_frame = ttk.Frame(notebook, padding=10)
        notebook.add(login_frame, text="Login")
        
        # Username
        ttk.Label(login_frame, text="Username:", font=("Arial", 10)).pack(pady=(10, 5), anchor=tk.W)
        self.login_username = tk.StringVar()
        login_user_entry = ttk.Entry(login_frame, textvariable=self.login_username, width=30)
        login_user_entry.pack(pady=5, fill=tk.X)
        login_user_entry.focus()
        
        # Password
        ttk.Label(login_frame, text="Password:", font=("Arial", 10)).pack(pady=(10, 5), anchor=tk.W)
        self.login_password = tk.StringVar()
        login_pass_entry = ttk.Entry(login_frame, textvariable=self.login_password, show="•", width=30)
        login_pass_entry.pack(pady=5, fill=tk.X)
        
        # Login button
        login_button = ttk.Button(
            login_frame, 
            text="Login", 
            command=self.login,
            style="Accent.TButton"
        )
        login_button.pack(pady=20, ipadx=20, ipady=5)
        
        # Register tab
        register_frame = ttk.Frame(notebook, padding=10)
        notebook.add(register_frame, text="Register")
        
        # Username
        ttk.Label(register_frame, text="Username:", font=("Arial", 10)).pack(pady=(10, 5), anchor=tk.W)
        self.reg_username = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_username, width=30).pack(pady=5, fill=tk.X)
        
        # Password
        ttk.Label(register_frame, text="Password:", font=("Arial", 10)).pack(pady=(10, 5), anchor=tk.W)
        self.reg_password = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_password, show="•", width=30).pack(pady=5, fill=tk.X)
        
        # Confirm Password
        ttk.Label(register_frame, text="Confirm Password:", font=("Arial", 10)).pack(pady=(10, 5), anchor=tk.W)
        self.reg_confirm = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_confirm, show="•", width=30).pack(pady=5, fill=tk.X)
        
        # Register button
        register_button = ttk.Button(
            register_frame, 
            text="Register", 
            command=self.register,
            style="Accent.TButton"
        )
        register_button.pack(pady=20, ipadx=20, ipady=5)
        
        # Configure styles
        self.configure_styles()
        
        # Bind tab change to clear fields
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure accent button
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#4CAF50",
            font=("Arial", 10, "bold")
        )
        style.map(
            "Accent.TButton",
            background=[('active', '#45a049')]
        )
    
    def on_tab_changed(self, event):
        """Clear fields when tab changes"""
        self.login_password.set("")
        self.reg_password.set("")
        self.reg_confirm.set("")
    
    def login(self):
        """Handle login"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username:
            messagebox.showwarning("Input Required", "Please enter username")
            return
        
        if not password:
            messagebox.showwarning("Input Required", "Please enter password")
            return
        
        # Show loading
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message = self.user_manager.authenticate_user(username, password)
        
        self.root.config(cursor="")
        
        if success:
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.root.destroy()
            self.open_main_app(username)
        else:
            messagebox.showerror("Login Failed", message)
    
    def register(self):
        """Handle registration"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        if not username:
            messagebox.showwarning("Input Required", "Please enter username")
            return
        
        if not password:
            messagebox.showwarning("Input Required", "Please enter password")
            return
        
        if not confirm:
            messagebox.showwarning("Input Required", "Please confirm password")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Show loading
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message = self.user_manager.register_user(username, password)
        
        self.root.config(cursor="")
        
        if success:
            messagebox.showinfo("Success", message)
            # Clear fields
            self.reg_username.set("")
            self.reg_password.set("")
            self.reg_confirm.set("")
            
            # Switch to login tab
            notebook = self.root.winfo_children()[2]  # Get the notebook widget
            notebook.select(0)  # Switch to first tab (login)
            
            # Auto-fill username in login
            self.login_username.set(username)
        else:
            messagebox.showerror("Registration Failed", message)
    
    def open_main_app(self, username):
        """Open the main application"""
        root = tk.Tk()
        task_manager = TaskManager(username, self.db_manager)
        app = TodoAppGUI(root, task_manager)
        
        # Center main window
        app.center_window(900, 700)
        
        root.mainloop()

def main():
    """Main entry point"""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()