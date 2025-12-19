"""
Command Line Interface for To-Do List Application
Optional implementation for terminal users
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from task_manager import TaskManager, Task
from user_manager import UserManager

class TodoCLI:
    """Command Line Interface for To-Do List"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.db_manager = DatabaseManager()
        self.current_user = None
        self.task_manager = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a formatted header"""
        self.clear_screen()
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)
        print()
    
    def print_menu(self, options: List[tuple[str, str]]):
        """Print a menu with options"""
        print("\n" + "-" * 60)
        for i, (key, description) in enumerate(options, 1):
            print(f"{i:2}. {description}")
        print("-" * 60)
    
    def get_choice(self, max_choice: int) -> int:
        """Get user choice with validation"""
        while True:
            try:
                choice = input("\nEnter your choice (1-" + str(max_choice) + "): ").strip()
                if not choice:
                    continue
                
                choice_num = int(choice)
                if 1 <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(f"Please enter a number between 1 and {max_choice}")
            except ValueError:
                print("Please enter a valid number")
    
    def login_screen(self):
        """Display login screen"""
        while True:
            self.print_header("To-Do List - Login")
            
            print("1. Login")
            print("2. Register")
            print("3. Exit")
            
            choice = self.get_choice(3)
            
            if choice == 1:
                self.login()
            elif choice == 2:
                self.register()
            elif choice == 3:
                print("\nGoodbye! 👋")
                sys.exit(0)
    
    def login(self):
        """Handle user login"""
        self.print_header("Login")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if not username or not password:
            input("\nUsername and password are required. Press Enter to continue...")
            return
        
        success, message = self.user_manager.authenticate_user(username, password)
        
        if success:
            self.current_user = username
            self.task_manager = TaskManager(username, self.db_manager)
            input(f"\n{message} Press Enter to continue...")
            self.main_menu()
        else:
            input(f"\n{message} Press Enter to continue...")
    
    def register(self):
        """Handle user registration"""
        self.print_header("Register")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        confirm = input("Confirm Password: ").strip()
        
        if password != confirm:
            input("\nPasswords do not match! Press Enter to continue...")
            return
        
        success, message = self.user_manager.register_user(username, password)
        
        input(f"\n{message} Press Enter to continue...")
    
    def main_menu(self):
        """Display main menu"""
        while True:
            self.print_header(f"To-Do List - Welcome, {self.current_user}!")
            
            stats = self.task_manager.get_task_statistics()
            
            print(f"📊 Statistics:")
            print(f"   Total Tasks: {stats['total_tasks']}")
            print(f"   Completed: {stats['completed_tasks']} ({stats['completion_rate']}%)")
            print(f"   Pending: {stats['pending_tasks']}")
            print(f"   Overdue: {stats['overdue_tasks']}")
            print()
            
            menu_options = [
                ("1", "View All Tasks"),
                ("2", "Add New Task"),
                ("3", "Search Tasks"),
                ("4", "View Statistics"),
                ("5", "Filter Tasks"),
                ("6", "Export Tasks"),
                ("7", "Logout")
            ]
            
            self.print_menu([(desc, desc) for _, desc in menu_options])
            choice = self.get_choice(7)
            
            if choice == 1:
                self.view_tasks()
            elif choice == 2:
                self.add_task()
            elif choice == 3:
                self.search_tasks()
            elif choice == 4:
                self.view_statistics()
            elif choice == 5:
                self.filter_tasks()
            elif choice == 6:
                self.export_tasks()
            elif choice == 7:
                self.current_user = None
                self.task_manager = None
                return
    
    def view_tasks(self, tasks: Optional[List[Task]] = None):
        """View tasks"""
        if tasks is None:
            tasks = self.task_manager.tasks
        
        if not tasks:
            input("\nNo tasks found. Press Enter to continue...")
            return
        
        self.print_header("View Tasks")
        
        # Sort by due date
        tasks = self.task_manager.sort_tasks(tasks, 'due_date')
        
        for i, task in enumerate(tasks, 1):
            status_icon = "✓" if task.status == "Completed" else "○"
            priority_icon = "⚡" if task.priority == "High" else "●"
            
            print(f"{i:3}. [{status_icon}] {priority_icon} {task.name}")
            
            # Show due date if available
            if task.due_date:
                days_left = task.days_until_due()
                if days_left is not None:
                    if task.status == "Completed":
                        date_info = "✓ Completed"
                    elif days_left < 0:
                        date_info = f"⚠️ Overdue by {-days_left} days"
                    elif days_left == 0:
                        date_info = "⏰ Due today"
                    elif days_left == 1:
                        date_info = "⏰ Due tomorrow"
                    else:
                        date_info = f"📅 Due in {days_left} days"
                    
                    due_date_str = task.due_date.strftime("%Y-%m-%d")
                    print(f"     Due: {due_date_str} ({date_info})")
            
            print(f"     Category: {task.category} | Priority: {task.priority}")
            
            if task.description:
                desc_preview = task.description[:50] + "..." if len(task.description) > 50 else task.description
                print(f"     Description: {desc_preview}")
            
            print()
        
        print(f"\nTotal: {len(tasks)} tasks")
        
        if tasks == self.task_manager.tasks:
            input("\nPress Enter to return to menu...")
        else:
            input("\nPress Enter to continue...")
    
    def add_task(self):
        """Add a new task"""
        self.print_header("Add New Task")
        
        name = input("Task Name: ").strip()
        if not name:
            input("\nTask name is required! Press Enter to continue...")
            return
        
        print("\nPriority levels:")
        print("1. High")
        print("2. Medium")
        print("3. Low")
        
        priority_choice = self.get_choice(3)
        priority = ["High", "Medium", "Low"][priority_choice - 1]
        
        print("\nCategories:")
        categories = ["Work", "Personal", "Study", "Health", "Finance", "Shopping", "General", "Other"]
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        category_choice = self.get_choice(len(categories))
        category = categories[category_choice - 1]
        
        due_date = None
        set_due_date = input("\nSet due date? (y/n): ").strip().lower()
        if set_due_date == 'y':
            date_str = input("Enter due date (YYYY-MM-DD): ").strip()
            try:
                due_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Task will be created without due date.")
        
        description = input("\nDescription (optional): ").strip()
        
        # Add the task
        success, message = self.task_manager.add_task(
            name=name,
            priority=priority,
            due_date=due_date,
            category=category,
            description=description
        )
        
        input(f"\n{message} Press Enter to continue...")
    
    def search_tasks(self):
        """Search for tasks"""
        self.print_header("Search Tasks")
        
        query = input("Enter search term: ").strip()
        if not query:
            input("\nPlease enter a search term. Press Enter to continue...")
            return
        
        results = self.task_manager.search_tasks(query)
        
        if not results:
            input(f"\nNo tasks found for '{query}'. Press Enter to continue...")
            return
        
        self.view_tasks(results)
    
    def view_statistics(self):
        """View detailed statistics"""
        self.print_header("Statistics")
        
        stats = self.task_manager.get_task_statistics()
        
        print("📊 Task Statistics")
        print("=" * 40)
        print()
        
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"Completed: {stats['completed_tasks']}")
        print(f"Pending: {stats['pending_tasks']}")
        print(f"Overdue: {stats['overdue_tasks']}")
        print(f"Due Soon (3 days): {stats['due_soon_tasks']}")
        print(f"Completion Rate: {stats['completion_rate']}%")
        print()
        
        print("📁 Categories:")
        print("-" * 40)
        for category, count in stats['categories'].items():
            percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            print(f"  {category}: {count} ({percentage:.1f}%)")
        print()
        
        print("⚡ Priorities:")
        print("-" * 40)
        for priority in ['High', 'Medium', 'Low']:
            count = stats['priorities'].get(priority, 0)
            percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            print(f"  {priority}: {count} ({percentage:.1f}%)")
        
        input("\nPress Enter to continue...")
    
    def filter_tasks(self):
        """Filter tasks by criteria"""
        self.print_header("Filter Tasks")
        
        print("Filter by:")
        print("1. Status (Pending/Completed)")
        print("2. Priority")
        print("3. Category")
        print("4. Overdue Tasks")
        print("5. Due Soon")
        
        choice = self.get_choice(5)
        
        if choice == 1:
            print("\nStatus:")
            print("1. Pending")
            print("2. Completed")
            status_choice = self.get_choice(2)
            status = "Pending" if status_choice == 1 else "Completed"
            tasks = self.task_manager.get_tasks_by_status(status)
            
        elif choice == 2:
            print("\nPriority:")
            print("1. High")
            print("2. Medium")
            print("3. Low")
            priority_choice = self.get_choice(3)
            priority = ["High", "Medium", "Low"][priority_choice - 1]
            tasks = self.task_manager.get_tasks_by_priority(priority)
            
        elif choice == 3:
            categories = list(set(task.category for task in self.task_manager.tasks))
            print("\nCategories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            if not categories:
                input("\nNo categories found. Press Enter to continue...")
                return
            
            category_choice = self.get_choice(len(categories))
            category = categories[category_choice - 1]
            tasks = self.task_manager.get_tasks_by_category(category)
            
        elif choice == 4:
            tasks = self.task_manager.get_overdue_tasks()
            
        elif choice == 5:
            tasks = self.task_manager.get_tasks_due_soon(3)
        
        if tasks:
            self.view_tasks(tasks)
        else:
            input("\nNo tasks found with the selected filter. Press Enter to continue...")
    
    def export_tasks(self):
        """Export tasks to file"""
        self.print_header("Export Tasks")
        
        print("Export format:")
        print("1. JSON")
        print("2. Text")
        
        format_choice = self.get_choice(2)
        format_type = "json" if format_choice == 1 else "txt"
        
        file_path = self.db_manager.export_user_tasks(self.current_user, format_type)
        
        if file_path:
            input(f"\nTasks exported to:\n{file_path}\n\nPress Enter to continue...")
        else:
            input("\nFailed to export tasks. Press Enter to continue...")
    
    def run(self):
        """Run the CLI application"""
        try:
            self.login_screen()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            input("\nPress Enter to exit...")
            sys.exit(1)

def main():
    """Main entry point for CLI"""
    cli = TodoCLI()
    cli.run()

if __name__ == "__main__":
    main()