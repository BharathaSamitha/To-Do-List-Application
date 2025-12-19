"""
GUI Implementation for To-Do List Application
Using Tkinter for the user interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import webbrowser
from typing import List, Optional, Dict, Any

from task_manager import Task, TaskManager

class TodoAppGUI:
    """Main GUI application for To-Do List"""
    
    def __init__(self, root: tk.Tk, task_manager: TaskManager):
        self.root = root
        self.task_manager = task_manager
        self.username = task_manager.username
        
        self.root.title(f"To-Do List - {self.username}")
        self.root.geometry("1000x700")
        
        # Configure styles
        self.setup_styles()
        
        # Variables
        self.filter_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="due_date")
        self.search_var = tk.StringVar()
        
        # Create UI
        self.create_menu()
        self.create_widgets()
        
        # Bind events
        self.bind_events()
        
        # Load initial data
        self.refresh_task_list()
        self.update_stats()
        
        # Focus on search box
        self.search_entry.focus()
    
    def center_window(self, width: int, height: int):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        # Configure styles
        style.configure('Primary.TButton', 
                       foreground='white',
                       background=self.colors['accent'],
                       font=('Arial', 10, 'bold'))
        
        style.configure('Success.TButton',
                       foreground='white',
                       background=self.colors['success'],
                       font=('Arial', 10, 'bold'))
        
        style.configure('Danger.TButton',
                       foreground='white',
                       background=self.colors['danger'],
                       font=('Arial', 10, 'bold'))
        
        style.configure('Stats.TLabel',
                       font=('Arial', 9),
                       padding=5)
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground=self.colors['primary'])
        
        # Configure treeview
        style.configure('Treeview',
                       rowheight=25,
                       font=('Arial', 10))
        
        style.configure('Treeview.Heading',
                       font=('Arial', 10, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', '#2980b9')])
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        style.map('Danger.TButton',
                 background=[('active', '#c0392b')])
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Tasks...", command=self.export_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Refresh", command=self.refresh_all, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Task menu
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tasks", menu=task_menu)
        task_menu.add_command(label="Add Task", command=self.open_add_task_dialog, accelerator="Ctrl+N")
        task_menu.add_command(label="Edit Task", command=self.edit_task, accelerator="Ctrl+E")
        task_menu.add_command(label="Delete Task", command=self.delete_task, accelerator="Delete")
        task_menu.add_separator()
        task_menu.add_command(label="Mark Completed", command=self.mark_completed, accelerator="Ctrl+M")
        task_menu.add_command(label="Mark Pending", command=self.mark_pending)
        task_menu.add_separator()
        task_menu.add_command(label="Clear Completed Tasks", command=self.clear_completed)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Statistics", command=self.show_statistics)
        view_menu.add_command(label="Show Overdue Tasks", command=self.show_overdue)
        view_menu.add_command(label="Show Due Soon", command=self.show_due_soon)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.refresh_all())
        self.root.bind('<Control-n>', lambda e: self.open_add_task_dialog())
        self.root.bind('<Control-e>', lambda e: self.edit_task())
        self.root.bind('<Delete>', lambda e: self.delete_task())
        self.root.bind('<Control-m>', lambda e: self.mark_completed())
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top bar (Search and Filters)
        top_bar = ttk.Frame(main_container)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Search box
        ttk.Label(top_bar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var.trace('w', self.on_search_changed)
        self.search_entry = ttk.Entry(top_bar, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Filter dropdown
        ttk.Label(top_bar, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        filter_combo = ttk.Combobox(top_bar, textvariable=self.filter_var, 
                                   values=["All", "Pending", "Completed", "Overdue", "Due Soon"],
                                   state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        # Sort dropdown
        ttk.Label(top_bar, text="Sort by:").pack(side=tk.LEFT, padx=(20, 5))
        sort_combo = ttk.Combobox(top_bar, textvariable=self.sort_var,
                                 values=["Due Date", "Priority", "Name", "Status", "Created"],
                                 state="readonly", width=15)
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.on_sort_changed)
        
        # Add Task button
        add_button = ttk.Button(top_bar, text="+ Add Task", 
                               command=self.open_add_task_dialog,
                               style="Primary.TButton")
        add_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_container, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create stats labels
        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        stats_data = [
            ("Total Tasks", "total"),
            ("Completed", "completed"),
            ("Pending", "pending"),
            ("Overdue", "overdue"),
            ("Due Soon", "due_soon"),
            ("Completion", "completion")
        ]
        
        for i, (label, key) in enumerate(stats_data):
            frame = ttk.Frame(stats_grid)
            frame.grid(row=0, column=i, padx=10, pady=5)
            
            ttk.Label(frame, text=label, style="Stats.TLabel").pack()
            value_label = ttk.Label(frame, text="0", font=("Arial", 14, "bold"))
            value_label.pack()
            
            self.stats_labels[key] = value_label
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Task list frame
        list_frame = ttk.LabelFrame(content_frame, text="Tasks", padding=10)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create treeview with scrollbar
        self.create_task_tree(list_frame)
        
        # Sidebar frame
        sidebar_frame = ttk.Frame(content_frame, width=250)
        sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)
        
        # Task details
        details_frame = ttk.LabelFrame(sidebar_frame, text="Task Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=10, 
                                                     font=("Arial", 10),
                                                     wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(sidebar_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(actions_frame, text="Mark Completed", 
                  command=self.mark_completed,
                  style="Success.TButton").pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="Mark Pending", 
                  command=self.mark_pending).pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="Edit Task", 
                  command=self.edit_task).pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="Delete Task", 
                  command=self.delete_task,
                  style="Danger.TButton").pack(fill=tk.X, pady=2)
        
        # Categories summary
        categories_frame = ttk.LabelFrame(sidebar_frame, text="Categories", padding=10)
        categories_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.categories_text = tk.Text(categories_frame, height=8, 
                                      font=("Arial", 9),
                                      wrap=tk.WORD)
        self.categories_text.pack(fill=tk.BOTH, expand=True)
        self.categories_text.config(state=tk.DISABLED)
    
    def create_task_tree(self, parent):
        """Create task treeview widget"""
        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("ID", "Name", "Priority", "Due Date", "Category", "Status", "Days Left")
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Define columns
        column_configs = [
            ("ID", 80, "c"),
            ("Name", 250, "w"),
            ("Priority", 80, "c"),
            ("Due Date", 100, "c"),
            ("Category", 100, "c"),
            ("Status", 100, "c"),
            ("Days Left", 80, "c")
        ]
        
        for col_text, width, anchor in column_configs:
            self.task_tree.heading(col_text, text=col_text)
            self.task_tree.column(col_text, width=width, anchor=anchor)
        
        # Hide ID column by default
        self.task_tree.column("ID", width=0, stretch=False)
        self.task_tree.heading("ID", text="")
        
        # Add scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_selected)
        self.task_tree.bind('<Double-Button-1>', lambda e: self.edit_task())
    
    def bind_events(self):
        """Bind keyboard and mouse events"""
        # Bind Enter key in search box
        self.search_entry.bind('<Return>', lambda e: self.refresh_task_list())
        
        # Bind Escape to clear search
        self.search_entry.bind('<Escape>', lambda e: self.clear_search())
    
    def clear_search(self):
        """Clear search box"""
        self.search_var.set("")
        self.refresh_task_list()
    
    def on_search_changed(self, *args):
        """Handle search text changes"""
        self.refresh_task_list()
    
    def on_filter_changed(self, event=None):
        """Handle filter changes"""
        self.refresh_task_list()
    
    def on_sort_changed(self, event=None):
        """Handle sort changes"""
        self.refresh_task_list()
    
    def on_task_selected(self, event=None):
        """Handle task selection"""
        selection = self.task_tree.selection()
        if not selection:
            self.clear_task_details()
            return
        
        item = self.task_tree.item(selection[0])
        task_id = item['values'][0]  # First value is task ID
        
        task = self.task_manager.get_task_by_id(task_id)
        if task:
            self.display_task_details(task)
    
    def clear_task_details(self):
        """Clear task details display"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "Select a task to view details...")
        self.details_text.config(state=tk.DISABLED)
    
    def display_task_details(self, task: Task):
        """Display task details in sidebar"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        # Format task details
        details = f"📋 {task.name}\n"
        details += "=" * 40 + "\n\n"
        
        details += f"📅 Status: {task.status}\n"
        details += f"⚡ Priority: {task.priority}\n"
        details += f"📁 Category: {task.category}\n\n"
        
        if task.due_date:
            due_date_str = task.due_date.strftime("%B %d, %Y")
            days_left = task.days_until_due()
            
            if task.status == 'Completed':
                details += f"✅ Completed\n"
            elif days_left is not None:
                if days_left < 0:
                    details += f"⚠️ Overdue by {-days_left} days\n"
                elif days_left == 0:
                    details += f"⏰ Due Today\n"
                elif days_left == 1:
                    details += f"⏰ Due Tomorrow\n"
                else:
                    details += f"📅 Due in {days_left} days\n"
            
            details += f"📅 Due Date: {due_date_str}\n"
        
        details += f"📝 Created: {task.created_at.strftime('%B %d, %Y')}\n"
        
        if task.description:
            details += "\n" + "=" * 40 + "\n"
            details += "Description:\n"
            details += "-" * 40 + "\n"
            details += task.description + "\n"
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
    
    def get_filtered_tasks(self) -> List[Task]:
        """Get tasks based on current filter and search"""
        tasks = self.task_manager.tasks
        
        # Apply search filter
        search_query = self.search_var.get().strip()
        if search_query:
            tasks = self.task_manager.search_tasks(search_query)
        
        # Apply status filter
        filter_value = self.filter_var.get()
        if filter_value == "Pending":
            tasks = self.task_manager.get_tasks_by_status("Pending")
        elif filter_value == "Completed":
            tasks = self.task_manager.get_tasks_by_status("Completed")
        elif filter_value == "Overdue":
            tasks = self.task_manager.get_overdue_tasks()
        elif filter_value == "Due Soon":
            tasks = self.task_manager.get_tasks_due_soon(3)
        
        # Apply sorting
        sort_map = {
            "Due Date": "due_date",
            "Priority": "priority",
            "Name": "name",
            "Status": "status",
            "Created": "created_at"
        }
        
        sort_key = sort_map.get(self.sort_var.get(), "due_date")
        tasks = self.task_manager.sort_tasks(tasks, sort_key)
        
        return tasks
    
    def refresh_task_list(self):
        """Refresh the task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get filtered and sorted tasks
        tasks = self.get_filtered_tasks()
        
        # Add tasks to treeview with formatting
        for task in tasks:
            # Format due date
            due_date_str = ""
            if task.due_date:
                due_date_str = task.due_date.strftime("%Y-%m-%d")
            
            # Calculate days left
            days_left = task.days_until_due()
            days_str = ""
            if days_left is not None:
                if task.status == 'Completed':
                    days_str = "✓"
                elif days_left < 0:
                    days_str = f"{-days_left}d ago"
                elif days_left == 0:
                    days_str = "Today"
                elif days_left == 1:
                    days_str = "Tomorrow"
                else:
                    days_str = f"{days_left}d"
            
            # Determine tag based on priority and status
            tags = []
            if task.priority == "High":
                tags.append("high")
            elif task.priority == "Low":
                tags.append("low")
            
            if task.status == "Completed":
                tags.append("completed")
            elif task.is_overdue():
                tags.append("overdue")
            
            # Insert task into treeview
            self.task_tree.insert("", tk.END, values=(
                task.id,
                task.name,
                task.priority,
                due_date_str,
                task.category,
                task.status,
                days_str
            ), tags=tags)
        
        # Update statistics
        self.update_stats()
        
        # Update categories display
        self.update_categories_display()
    
    def update_stats(self):
        """Update statistics display"""
        stats = self.task_manager.get_task_statistics()
        
        self.stats_labels['total'].config(text=str(stats['total_tasks']))
        self.stats_labels['completed'].config(text=str(stats['completed_tasks']))
        self.stats_labels['pending'].config(text=str(stats['pending_tasks']))
        self.stats_labels['overdue'].config(text=str(stats['overdue_tasks']))
        self.stats_labels['due_soon'].config(text=str(stats['due_soon_tasks']))
        self.stats_labels['completion'].config(text=f"{stats['completion_rate']}%")
    
    def update_categories_display(self):
        """Update categories display in sidebar"""
        stats = self.task_manager.get_task_statistics()
        categories = stats.get('categories', {})
        
        self.categories_text.config(state=tk.NORMAL)
        self.categories_text.delete(1.0, tk.END)
        
        if not categories:
            self.categories_text.insert(1.0, "No categories yet")
        else:
            # Sort categories by count
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            for category, count in sorted_categories:
                percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
                bar_length = int(percentage / 5)  # Scale for display
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                line = f"{category:<15} {count:>3} {bar} {percentage:.1f}%\n"
                self.categories_text.insert(tk.END, line)
        
        self.categories_text.config(state=tk.DISABLED)
    
    def refresh_all(self):
        """Refresh everything"""
        self.task_manager.load_tasks()
        self.refresh_task_list()
        self.clear_task_details()
    
    def get_selected_task_id(self) -> Optional[str]:
        """Get ID of selected task"""
        selection = self.task_tree.selection()
        if not selection:
            return None
        
        item = self.task_tree.item(selection[0])
        return item['values'][0]  # First value is task ID
    
    def open_add_task_dialog(self):
        """Open dialog to add new task"""
        AddTaskDialog(self.root, self.task_manager, self)
    
    def edit_task(self):
        """Edit selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return
        
        task = self.task_manager.get_task_by_id(task_id)
        if task:
            EditTaskDialog(self.root, self.task_manager, task, self)
    
    def delete_task(self):
        """Delete selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to delete")
            return
        
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete task:\n\n'{task.name}'?")
        
        if confirm:
            success, message = self.task_manager.delete_task(task_id)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_all()
            else:
                messagebox.showerror("Error", message)
    
    def mark_completed(self):
        """Mark selected task as completed"""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to mark as completed")
            return
        
        success, message = self.task_manager.mark_completed(task_id)
        if success:
            self.refresh_all()
            # Don't show message box for single task completion
        else:
            messagebox.showerror("Error", message)
    
    def mark_pending(self):
        """Mark selected task as pending"""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to mark as pending")
            return
        
        success, message = self.task_manager.mark_pending(task_id)
        if success:
            self.refresh_all()
        else:
            messagebox.showerror("Error", message)
    
    def clear_completed(self):
        """Clear all completed tasks"""
        confirm = messagebox.askyesno("Confirm Clear", 
                                     "Are you sure you want to clear all completed tasks?")
        
        if confirm:
            success, message = self.task_manager.clear_completed_tasks()
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_all()
            else:
                messagebox.showerror("Error", message)
    
    def export_tasks(self):
        """Export tasks to file"""
        ExportDialog(self.root, self.task_manager)
    
    def show_statistics(self):
        """Show detailed statistics"""
        stats = self.task_manager.get_task_statistics()
        
        stats_text = f"📊 Task Statistics for {self.username}\n"
        stats_text += "=" * 40 + "\n\n"
        
        stats_text += f"📋 Total Tasks: {stats['total_tasks']}\n"
        stats_text += f"✅ Completed: {stats['completed_tasks']}\n"
        stats_text += f"⏳ Pending: {stats['pending_tasks']}\n"
        stats_text += f"⚠️ Overdue: {stats['overdue_tasks']}\n"
        stats_text += f"⏰ Due Soon (3 days): {stats['due_soon_tasks']}\n"
        stats_text += f"📈 Completion Rate: {stats['completion_rate']}%\n\n"
        
        stats_text += "📁 Categories:\n"
        for category, count in stats['categories'].items():
            percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            stats_text += f"  {category}: {count} ({percentage:.1f}%)\n"
        
        stats_text += "\n⚡ Priorities:\n"
        for priority in ['High', 'Medium', 'Low']:
            count = stats['priorities'].get(priority, 0)
            percentage = (count / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            stats_text += f"  {priority}: {count} ({percentage:.1f}%)\n"
        
        # Show in message box
        messagebox.showinfo("Task Statistics", stats_text)
    
    def show_overdue(self):
        """Show overdue tasks"""
        overdue_tasks = self.task_manager.get_overdue_tasks()
        
        if not overdue_tasks:
            messagebox.showinfo("Overdue Tasks", "No overdue tasks! 🎉")
            return
        
        tasks_text = f"⚠️ Overdue Tasks ({len(overdue_tasks)})\n"
        tasks_text += "=" * 40 + "\n\n"
        
        for i, task in enumerate(overdue_tasks, 1):
            days_overdue = -task.days_until_due() if task.days_until_due() else 0
            tasks_text += f"{i}. {task.name}\n"
            tasks_text += f"   Due: {task.due_date.strftime('%Y-%m-%d')} ({days_overdue} days ago)\n"
            tasks_text += f"   Priority: {task.priority}\n\n"
        
        messagebox.showinfo("Overdue Tasks", tasks_text)
    
    def show_due_soon(self):
        """Show tasks due soon"""
        due_soon_tasks = self.task_manager.get_tasks_due_soon(3)
        
        if not due_soon_tasks:
            messagebox.showinfo("Due Soon", "No tasks due in the next 3 days!")
            return
        
        tasks_text = f"⏰ Tasks Due Soon ({len(due_soon_tasks)})\n"
        tasks_text += "=" * 40 + "\n\n"
        
        for i, task in enumerate(due_soon_tasks, 1):
            days_left = task.days_until_due()
            days_text = "Today" if days_left == 0 else f"{days_left} days"
            
            tasks_text += f"{i}. {task.name}\n"
            tasks_text += f"   Due: {task.due_date.strftime('%Y-%m-%d')} ({days_text})\n"
            tasks_text += f"   Priority: {task.priority}\n\n"
        
        messagebox.showinfo("Tasks Due Soon", tasks_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """📋 To-Do List Application - Help

🔑 **Login/Register:**
   - First time? Click Register tab
   - Returning user? Click Login tab

➕ **Adding Tasks:**
   - Click "+ Add Task" button
   - Press Ctrl+N
   - Use menu: Tasks → Add Task

✏️ **Editing Tasks:**
   - Select task and click "Edit Task"
   - Press Ctrl+E
   - Double-click task

🗑️ **Deleting Tasks:**
   - Select task and click "Delete Task"
   - Press Delete key

✅ **Marking Tasks:**
   - Select task and click "Mark Completed"
   - Press Ctrl+M
   - Use Quick Actions in sidebar

🔍 **Search & Filter:**
   - Type in search box to find tasks
   - Use dropdowns to filter by status
   - Sort by different criteria

📊 **Statistics:**
   - View → Show Statistics
   - See completion rates and categories

📤 **Export:**
   - File → Export Tasks
   - Export to JSON or text format

💡 **Tips:**
   - Press F5 to refresh
   - Use keyboard shortcuts for efficiency
   - Check "Due Soon" regularly
"""
        
        messagebox.showinfo("User Guide", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """📋 To-Do List Application
Version 1.0

A feature-rich task management application
built with Python and Tkinter.

✨ Features:
• User authentication
• Task management (CRUD)
• Priority levels
• Due dates and reminders
• Categories and tags
• Search and filtering
• Statistics and insights
• Data export

👨‍💻 Developer: Bharatha Samitha
📧 Email: samithabharatha@gmail.com
📅 Date: December 2025

Built with ❤️ using Python"""
        
        messagebox.showinfo("About", about_text)


class AddTaskDialog:
    """Dialog for adding new tasks"""
    
    def __init__(self, parent, task_manager, callback):
        self.parent = parent
        self.task_manager = task_manager
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Task")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog(500, 500)
        
        self.create_widgets()
    
    def center_dialog(self, width, height):
        """Center dialog on parent"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Add New Task", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Task name
        ttk.Label(main_frame, text="Task Name *", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=("Arial", 11))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        # Priority and Category
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Priority
        ttk.Label(details_frame, text="Priority", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(details_frame, textvariable=self.priority_var,
                                     values=["High", "Medium", "Low"], 
                                     state="readonly", width=15)
        priority_combo.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(details_frame, text="Category", 
                 font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W)
        self.category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(details_frame, textvariable=self.category_var,
                                     values=["Work", "Personal", "Study", "Health", 
                                             "Finance", "Shopping", "General", "Other"],
                                     state="readonly", width=15)
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Due Date
        ttk.Label(main_frame, text="Due Date", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.due_date_var = tk.StringVar()
        
        # Date entry
        self.date_entry = DateEntry(date_frame, width=15, 
                                   date_pattern='yyyy-mm-dd',
                                   font=("Arial", 10))
        self.date_entry.pack(side=tk.LEFT)
        
        # Quick date buttons
        quick_dates_frame = ttk.Frame(date_frame)
        quick_dates_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(quick_dates_frame, text="Today", 
                  command=lambda: self.set_date(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Tomorrow", 
                  command=lambda: self.set_date(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Next Week", 
                  command=lambda: self.set_date(7)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Clear", 
                  command=self.clear_date).pack(side=tk.LEFT, padx=2)
        
        # Description
        ttk.Label(main_frame, text="Description", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        self.desc_text = scrolledtext.ScrolledText(main_frame, height=8, 
                                                  font=("Arial", 10),
                                                  wrap=tk.WORD)
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Add Task", 
                  command=self.add_task,
                  style="Primary.TButton").pack(side=tk.RIGHT)
        
        # Bind Enter key to add task
        self.dialog.bind('<Return>', lambda e: self.add_task())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def set_date(self, days_offset):
        """Set date with offset from today"""
        from datetime import datetime, timedelta
        new_date = datetime.now() + timedelta(days=days_offset)
        self.date_entry.set_date(new_date)
    
    def clear_date(self):
        """Clear date selection"""
        self.date_entry.set_date(None)
    
    def add_task(self):
        """Add the new task"""
        # Get values
        name = self.name_var.get().strip()
        priority = self.priority_var.get()
        category = self.category_var.get()
        due_date = self.date_entry.get_date()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        # Validate
        if not name:
            messagebox.showwarning("Validation", "Task name is required!")
            return
        
        # Add task
        success, message = self.task_manager.add_task(
            name=name,
            priority=priority,
            due_date=due_date,
            category=category,
            description=description
        )
        
        if success:
            self.dialog.destroy()
            self.callback.refresh_all()
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


class EditTaskDialog:
    """Dialog for editing tasks"""
    
    def __init__(self, parent, task_manager, task, callback):
        self.parent = parent
        self.task_manager = task_manager
        self.task = task
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Task: {task.name}")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog(500, 500)
        
        self.create_widgets()
        self.load_task_data()
    
    def center_dialog(self, width, height):
        """Center dialog on parent"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Edit Task", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Task name
        ttk.Label(main_frame, text="Task Name *", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=("Arial", 11))
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        # Priority, Category, and Status
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Priority
        ttk.Label(details_frame, text="Priority", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(details_frame, textvariable=self.priority_var,
                                     values=["High", "Medium", "Low"], 
                                     state="readonly", width=15)
        priority_combo.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(details_frame, text="Category", 
                 font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(details_frame, textvariable=self.category_var,
                                     values=["Work", "Personal", "Study", "Health", 
                                             "Finance", "Shopping", "General", "Other"],
                                     state="readonly", width=15)
        category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Status
        ttk.Label(details_frame, text="Status", 
                 font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(details_frame, textvariable=self.status_var,
                                   values=["Pending", "In Progress", "Completed", "Cancelled"],
                                   state="readonly", width=15)
        status_combo.grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # Due Date
        ttk.Label(main_frame, text="Due Date", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Date entry
        self.date_entry = DateEntry(date_frame, width=15, 
                                   date_pattern='yyyy-mm-dd',
                                   font=("Arial", 10))
        self.date_entry.pack(side=tk.LEFT)
        
        # Quick date buttons
        quick_dates_frame = ttk.Frame(date_frame)
        quick_dates_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(quick_dates_frame, text="Today", 
                  command=lambda: self.set_date(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Tomorrow", 
                  command=lambda: self.set_date(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Next Week", 
                  command=lambda: self.set_date(7)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Clear", 
                  command=self.clear_date).pack(side=tk.LEFT, padx=2)
        
        # Description
        ttk.Label(main_frame, text="Description", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        self.desc_text = scrolledtext.ScrolledText(main_frame, height=8, 
                                                  font=("Arial", 10),
                                                  wrap=tk.WORD)
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_task,
                  style="Primary.TButton").pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save_task())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def load_task_data(self):
        """Load task data into form"""
        self.name_var.set(self.task.name)
        self.priority_var.set(self.task.priority)
        self.category_var.set(self.task.category)
        self.status_var.set(self.task.status)
        
        if self.task.due_date:
            self.date_entry.set_date(self.task.due_date)
        
        if self.task.description:
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, self.task.description)
    
    def set_date(self, days_offset):
        """Set date with offset from today"""
        from datetime import datetime, timedelta
        new_date = datetime.now() + timedelta(days=days_offset)
        self.date_entry.set_date(new_date)
    
    def clear_date(self):
        """Clear date selection"""
        self.date_entry.set_date(None)
    
    def save_task(self):
        """Save task changes"""
        # Get values
        name = self.name_var.get().strip()
        priority = self.priority_var.get()
        category = self.category_var.get()
        status = self.status_var.get()
        due_date = self.date_entry.get_date()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        # Validate
        if not name:
            messagebox.showwarning("Validation", "Task name is required!")
            return
        
        # Update task
        success, message = self.task_manager.update_task(
            self.task.id,
            name=name,
            priority=priority,
            category=category,
            status=status,
            due_date=due_date,
            description=description
        )
        
        if success:
            self.dialog.destroy()
            self.callback.refresh_all()
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


class ExportDialog:
    """Dialog for exporting tasks"""
    
    def __init__(self, parent, task_manager):
        self.parent = parent
        self.task_manager = task_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Tasks")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog(400, 300)
        
        self.create_widgets()
    
    def center_dialog(self, width, height):
        """Center dialog on parent"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Export Tasks", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Format selection
        ttk.Label(main_frame, text="Export Format:", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="json")
        
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(format_frame, text="JSON Format", 
                       variable=self.format_var, value="json").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(format_frame, text="Text Format", 
                       variable=self.format_var, value="txt").pack(anchor=tk.W, pady=5)
        
        # Include options
        ttk.Label(main_frame, text="Include:", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        self.include_completed_var = tk.BooleanVar(value=True)
        self.include_pending_var = tk.BooleanVar(value=True)
        
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Checkbutton(options_frame, text="Completed Tasks", 
                       variable=self.include_completed_var).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(options_frame, text="Pending Tasks", 
                       variable=self.include_pending_var).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Export", 
                  command=self.export_tasks,
                  style="Primary.TButton").pack(side=tk.RIGHT)
    
    def export_tasks(self):
        """Export tasks to file"""
        from database import DatabaseManager
        
        db = DatabaseManager()
        format_type = self.format_var.get()
        
        # Get tasks to export based on selection
        tasks_to_export = []
        
        if self.include_completed_var.get():
            tasks_to_export.extend(self.task_manager.get_tasks_by_status("Completed"))
        
        if self.include_pending_var.get():
            tasks_to_export.extend(self.task_manager.get_tasks_by_status("Pending"))
        
        # If nothing selected, export all
        if not tasks_to_export:
            tasks_to_export = self.task_manager.tasks
        
        # Convert to dictionary format
        tasks_data = [task.to_dict() for task in tasks_to_export]
        
        # Export
        if format_type == 'json':
            file_path = db.export_user_tasks(self.task_manager.username, 'json')
            if file_path:
                messagebox.showinfo("Export Successful", 
                                  f"Tasks exported to:\n{file_path}")
            else:
                messagebox.showerror("Export Failed", "Failed to export tasks")
        
        elif format_type == 'txt':
            file_path = db.export_user_tasks(self.task_manager.username, 'txt')
            if file_path:
                messagebox.showinfo("Export Successful", 
                                  f"Tasks exported to:\n{file_path}")
            else:
                messagebox.showerror("Export Failed", "Failed to export tasks")
        
        self.dialog.destroy()