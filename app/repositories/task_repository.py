import sqlite3
from typing import List, Optional
from datetime import datetime
from app.models.task import Task

class TaskRepository:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._init_db()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def _get_connection(self):
        if self.db_url.startswith('sqlite:///'):
            return sqlite3.connect(self.db_url.split('///')[1])
        raise ValueError("Unsupported database URL")

    def add_task(self, task: Task) -> Optional[Task]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    '''INSERT INTO tasks (description, priority, created_by) 
                    VALUES (?, ?, ?) RETURNING id, created_at''',
                    (task.description, task.priority, task.created_by)
                )
                row = cursor.fetchone()
                if row:
                    return Task(
                        id=row[0],
                        description=task.description,
                        priority=task.priority,
                        created_by=task.created_by,
                        created_at=datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                    )
        except Exception as e:
            print(f"Error adding task: {e}")
            return None

    def get_all_tasks(self) -> List[Task]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    '''SELECT id, description, priority, created_by, created_at 
                    FROM tasks ORDER BY 
                    CASE priority
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'Low' THEN 3
                    END, created_at'''
                )
                return [
                    Task(
                        id=row[0],
                        description=row[1],
                        priority=row[2],
                        created_by=row[3],
                        created_at=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    ) for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    def get_task(self, task_id: int) -> Optional[Task]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    '''SELECT id, description, priority, created_by, created_at 
                    FROM tasks WHERE id = ?''',
                    (task_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Task(
                        id=row[0],
                        description=row[1],
                        priority=row[2],
                        created_by=row[3],
                        created_at=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    )
        except Exception as e:
            print(f"Error getting task {task_id}: {e}")
            return None

    def update_task(self, task: Task) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    '''UPDATE tasks SET 
                    description = ?, 
                    priority = ? 
                    WHERE id = ?''',
                    (task.description, task.priority, task.id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating task {task.id}: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    'DELETE FROM tasks WHERE id = ?',
                    (task_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting task {task_id}: {e}")
            return False
