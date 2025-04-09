import sqlite3
from dataclasses import dataclass
from typing import List

@dataclass
class Task:
    id: int
    user_id: int
    description: str
    priority: int  # 1=Low, 2=Medium, 3=High

class TaskDatabase:
    def __init__(self, db_name='tasks.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            priority INTEGER NOT NULL
        )
        ''')
        self.conn.commit()

    def add_task(self, user_id: int, description: str, priority: int) -> Task:
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO tasks (user_id, description, priority)
        VALUES (?, ?, ?)
        ''', (user_id, description, priority))
        self.conn.commit()
        return Task(cursor.lastrowid, user_id, description, priority)

    def get_tasks(self, user_id: int) -> List[Task]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, user_id, description, priority FROM tasks
        WHERE user_id = ?
        ORDER BY priority DESC, id
        ''', (user_id,))
        return [Task(*row) for row in cursor.fetchall()]

    def delete_task(self, user_id: int, task_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('''
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
        ''', (task_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def edit_task(self, user_id: int, task_id: int, description: str = None, priority: int = None) -> bool:
        if not description and not priority:
            return False

        updates = []
        params = []
        
        if description:
            updates.append("description = ?")
            params.append(description)
        if priority:
            updates.append("priority = ?")
            params.append(priority)
        
        params.extend([task_id, user_id])
        
        query = f'''
        UPDATE tasks
        SET {', '.join(updates)}
        WHERE id = ? AND user_id = ?
        '''
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        self.conn.close()
