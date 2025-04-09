from typing import List, Optional
from app.models.task import Task
from app.repositories.task_repository import TaskRepository

class TaskService:
    PRIORITIES = ['High', 'Medium', 'Low']

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, description: str, priority: str, created_by: str) -> Optional[Task]:
        if priority not in self.PRIORITIES:
            priority = 'Medium'
        return self.repository.add_task(
            Task(description=description, priority=priority, created_by=created_by)
        )

    def get_all_tasks(self) -> List[Task]:
        return self.repository.get_all_tasks()

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.repository.get_task(task_id)

    def update_task_description(self, task_id: int, new_description: str) -> bool:
        task = self.repository.get_task(task_id)
        if not task:
            return False
        task.description = new_description
        return self.repository.update_task(task)

    def update_task_priority(self, task_id: int, new_priority: str) -> bool:
        if new_priority not in self.PRIORITIES:
            return False
        task = self.repository.get_task(task_id)
        if not task:
            return False
        task.priority = new_priority
        return self.repository.update_task(task)

    def delete_task(self, task_id: int) -> bool:
        return self.repository.delete_task(task_id)
