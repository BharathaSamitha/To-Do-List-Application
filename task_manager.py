"""
Task Manager for To-Do List Application
Handles all task-related operations
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid

class Task:
    """Represents a single task"""
    
    def __init__(self, 
                 name: str, 
                 priority: str = "Medium", 
                 due_date: Optional[datetime] = None, 
                 category: str = "General", 
                 status: str = "Pending",
                 description: str = ""):
        
        self.id = str(uuid.uuid4())[:8]  # Generate unique ID
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.status = status
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Set default due date if not provided (7 days from now)
        if not due_date:
            self.due_date = datetime.now() + timedelta(days=7)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.status})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for storage"""
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'category': self.category,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        # Parse dates
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'])
            except (ValueError, TypeError):
                pass
        
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
        
        updated_at = datetime.now()
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                pass
        
        # Create task
        task = cls(
            name=data['name'],
            priority=data.get('priority', 'Medium'),
            due_date=due_date,
            category=data.get('category', 'General'),
            status=data.get('status', 'Pending'),
            description=data.get('description', '')
        )
        
        # Set IDs and timestamps
        task.id = data.get('id', task.id)
        task.created_at = created_at
        task.updated_at = updated_at
        
        return task
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == 'Completed':
            return False
        return self.due_date < datetime.now()
    
    def days_until_due(self) -> Optional[int]:
        """Get days until due date"""
        if not self.due_date:
            return None
        
        delta = self.due_date.date() - datetime.now().date()
        return delta.days
    
    def get_priority_color(self) -> str:
        """Get color code for priority"""
        colors = {
            'High': '#ff4444',    # Red
            'Medium': '#ffbb33',  # Yellow
            'Low': '#00C851'      # Green
        }
        return colors.get(self.priority, '#ffbb33')
    
    def get_status_icon(self) -> str:
        """Get icon for status"""
        icons = {
            'Pending': '○',
            'In Progress': '↻',
            'Completed': '✓',
            'Cancelled': '✗'
        }
        return icons.get(self.status, '○')

class TaskManager:
    """Manages all tasks for a user"""
    
    def __init__(self, username: str, db_manager):
        self.username = username
        self.db = db_manager
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from database"""
        tasks_data = self.db.load_user_tasks(self.username)
        self.tasks = [Task.from_dict(task_data) for task_data in tasks_data]
    
    def save_tasks(self) -> bool:
        """Save tasks to database"""
        tasks_data = [task.to_dict() for task in self.tasks]
        return self.db.save_user_tasks(self.username, tasks_data)
    
    def add_task(self, name: str, priority: str = "Medium", 
                 due_date: Optional[datetime] = None, 
                 category: str = "General",
                 description: str = "") -> tuple[bool, str]:
        """Add a new task"""
        try:
            # Validate inputs
            if not name or not name.strip():
                return False, "Task name cannot be empty"
            
            if len(name.strip()) > 200:
                return False, "Task name is too long (max 200 characters)"
            
            # Create and add task
            task = Task(
                name=name.strip(),
                priority=priority,
                due_date=due_date,
                category=category,
                description=description
            )
            
            self.tasks.append(task)
            
            # Save to database
            if self.save_tasks():
                return True, f"Task '{name}' added successfully"
            else:
                # Rollback if save fails
                self.tasks.remove(task)
                return False, "Failed to save task to database"
        
        except Exception as e:
            return False, f"Error adding task: {str(e)}"
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> tuple[bool, str]:
        """Update task properties"""
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                return False, "Task not found"
            
            # Validate name if provided
            if 'name' in kwargs and kwargs['name']:
                name = kwargs['name'].strip()
                if not name:
                    return False, "Task name cannot be empty"
                if len(name) > 200:
                    return False, "Task name is too long (max 200 characters)"
                kwargs['name'] = name
            
            # Update task properties
            for key, value in kwargs.items():
                if hasattr(task, key) and value is not None:
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            
            # Save changes
            if self.save_tasks():
                return True, "Task updated successfully"
            else:
                return False, "Failed to save changes"
        
        except Exception as e:
            return False, f"Error updating task: {str(e)}"
    
    def delete_task(self, task_id: str) -> tuple[bool, str]:
        """Delete a task"""
        try:
            task = self.get_task_by_id(task_id)
            if not task:
                return False, "Task not found"
            
            task_name = task.name
            self.tasks.remove(task)
            
            if self.save_tasks():
                return True, f"Task '{task_name}' deleted successfully"
            else:
                # Rollback if save fails
                self.tasks.append(task)
                return False, "Failed to save changes"
        
        except Exception as e:
            return False, f"Error deleting task: {str(e)}"
    
    def mark_completed(self, task_id: str) -> tuple[bool, str]:
        """Mark task as completed"""
        return self.update_task(task_id, status="Completed")
    
    def mark_pending(self, task_id: str) -> tuple[bool, str]:
        """Mark task as pending"""
        return self.update_task(task_id, status="Pending")
    
    def get_tasks_by_status(self, status: str = None) -> List[Task]:
        """Get tasks filtered by status"""
        if status:
            return [task for task in self.tasks if task.status == status]
        return self.tasks
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks filtered by category"""
        return [task for task in self.tasks if task.category == category]
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get tasks filtered by priority"""
        return [task for task in self.tasks if task.priority == priority]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        return [task for task in self.tasks if task.is_overdue() and task.status != 'Completed']
    
    def get_tasks_due_soon(self, days: int = 3) -> List[Task]:
        """Get tasks due within specified days"""
        today = datetime.now().date()
        due_date = today + timedelta(days=days)
        
        due_soon = []
        for task in self.tasks:
            if task.due_date and task.status != 'Completed':
                task_due_date = task.due_date.date()
                if today <= task_due_date <= due_date:
                    due_soon.append(task)
        
        return due_soon
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status('Completed'))
        pending = len(self.get_tasks_by_status('Pending'))
        overdue = len(self.get_overdue_tasks())
        due_soon = len(self.get_tasks_due_soon(3))
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Category breakdown
        categories = {}
        for task in self.tasks:
            category = task.category
            categories[category] = categories.get(category, 0) + 1
        
        # Priority breakdown
        priorities = {'High': 0, 'Medium': 0, 'Low': 0}
        for task in self.tasks:
            priorities[task.priority] = priorities.get(task.priority, 0) + 1
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'overdue_tasks': overdue,
            'due_soon_tasks': due_soon,
            'completion_rate': round(completion_rate, 2),
            'categories': categories,
            'priorities': priorities
        }
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by name or description"""
        query = query.lower().strip()
        if not query:
            return self.tasks
        
        results = []
        for task in self.tasks:
            if (query in task.name.lower() or 
                query in task.description.lower() or
                query in task.category.lower()):
                results.append(task)
        
        return results
    
    def sort_tasks(self, tasks: List[Task], sort_by: str = 'due_date') -> List[Task]:
        """Sort tasks by specified criteria"""
        if sort_by == 'due_date':
            return sorted(tasks, key=lambda x: x.due_date or datetime.max)
        elif sort_by == 'priority':
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            return sorted(tasks, key=lambda x: priority_order.get(x.priority, 3))
        elif sort_by == 'name':
            return sorted(tasks, key=lambda x: x.name.lower())
        elif sort_by == 'created_at':
            return sorted(tasks, key=lambda x: x.created_at, reverse=True)
        elif sort_by == 'status':
            status_order = {'Pending': 0, 'In Progress': 1, 'Completed': 2, 'Cancelled': 3}
            return sorted(tasks, key=lambda x: status_order.get(x.status, 4))
        else:
            return tasks
    
    def clear_completed_tasks(self) -> tuple[bool, str]:
        """Remove all completed tasks"""
        try:
            completed_tasks = self.get_tasks_by_status('Completed')
            if not completed_tasks:
                return True, "No completed tasks to remove"
            
            # Remove completed tasks
            self.tasks = [task for task in self.tasks if task.status != 'Completed']
            
            if self.save_tasks():
                return True, f"Removed {len(completed_tasks)} completed tasks"
            else:
                # Rollback if save fails
                self.load_tasks()
                return False, "Failed to save changes"
        
        except Exception as e:
            return False, f"Error clearing completed tasks: {str(e)}"