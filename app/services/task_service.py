from typing import List, Optional
from app.models.task import Task
from app.repositories.task_repository import TaskRepository

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, description: str, priority: str, created_by: str) -> Optional[Task]:
        task = Task(id=None, description=description, priority=priority, created_by=created_by)
        return self.repository.add_task(task)

    def get_all_tasks(self) -> List[Task]:
        return self.repository.get_all_tasks()

    # ... other service methods
