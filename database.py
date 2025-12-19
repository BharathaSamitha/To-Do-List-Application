"""
Database Manager for To-Do List Application
Handles JSON file storage for tasks and users
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import shutil

class DatabaseManager:
    """Manages all database operations for the application"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tasks_dir = os.path.join(data_dir, "tasks")
        self.backup_dir = os.path.join(data_dir, "backups")
        
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.data_dir, self.tasks_dir, self.backup_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def save_user_tasks(self, username: str, tasks: List[Dict]) -> bool:
        """Save tasks for a specific user"""
        try:
            filepath = os.path.join(self.tasks_dir, f"{username}_tasks.json")
            
            # Create backup before saving
            self.create_backup(username)
            
            # Prepare tasks for JSON serialization
            serializable_tasks = []
            for task in tasks:
                serializable_task = task.copy()
                # Convert datetime objects to strings
                for key, value in task.items():
                    if isinstance(value, datetime):
                        serializable_task[key] = value.isoformat()
                serializable_tasks.append(serializable_task)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_tasks, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error saving tasks for {username}: {e}")
            return False
    
    def load_user_tasks(self, username: str) -> List[Dict]:
        """Load tasks for a specific user"""
        try:
            filepath = os.path.join(self.tasks_dir, f"{username}_tasks.json")
            
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # Convert date strings back to datetime objects
            for task in tasks:
                for key, value in task.items():
                    if isinstance(value, str) and 'date' in key.lower():
                        try:
                            task[key] = datetime.fromisoformat(value)
                        except (ValueError, TypeError):
                            pass
            
            return tasks
        
        except Exception as e:
            print(f"Error loading tasks for {username}: {e}")
            return []
    
    def create_backup(self, username: str):
        """Create a backup of user's tasks"""
        try:
            source = os.path.join(self.tasks_dir, f"{username}_tasks.json")
            if os.path.exists(source):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{username}_tasks_backup_{timestamp}.json"
                destination = os.path.join(self.backup_dir, backup_file)
                shutil.copy2(source, destination)
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def get_user_stats(self, username: str) -> Dict[str, Any]:
        """Get statistics for a user"""
        tasks = self.load_user_tasks(username)
        
        if not tasks:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "completion_rate": 0
            }
        
        total = len(tasks)
        completed = sum(1 for task in tasks if task.get('status') == 'Completed')
        pending = total - completed
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": round(completion_rate, 2)
        }
    
    def export_user_tasks(self, username: str, format: str = 'json') -> Optional[str]:
        """Export user tasks to a file"""
        try:
            tasks = self.load_user_tasks(username)
            
            if format.lower() == 'json':
                export_file = os.path.join(self.data_dir, f"{username}_tasks_export.json")
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(tasks, f, indent=2, ensure_ascii=False)
                return export_file
            
            elif format.lower() == 'txt':
                export_file = os.path.join(self.data_dir, f"{username}_tasks_export.txt")
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write(f"Tasks for {username}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, task in enumerate(tasks, 1):
                        f.write(f"Task #{i}\n")
                        f.write(f"  Name: {task.get('name', 'N/A')}\n")
                        f.write(f"  Priority: {task.get('priority', 'N/A')}\n")
                        f.write(f"  Category: {task.get('category', 'N/A')}\n")
                        f.write(f"  Status: {task.get('status', 'N/A')}\n")
                        
                        due_date = task.get('due_date')
                        if due_date:
                            if isinstance(due_date, datetime):
                                f.write(f"  Due Date: {due_date.strftime('%Y-%m-%d')}\n")
                            else:
                                f.write(f"  Due Date: {due_date}\n")
                        
                        created = task.get('created_at')
                        if created:
                            if isinstance(created, datetime):
                                f.write(f"  Created: {created.strftime('%Y-%m-%d %H:%M')}\n")
                            else:
                                f.write(f"  Created: {created}\n")
                        
                        f.write("\n")
                
                return export_file
            
            return None
        
        except Exception as e:
            print(f"Error exporting tasks: {e}")
            return None
    
    def cleanup_old_backups(self, days: int = 30):
        """Clean up backups older than specified days"""
        try:
            current_time = datetime.now().timestamp()
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > (days * 24 * 60 * 60):  # Convert days to seconds
                        os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")