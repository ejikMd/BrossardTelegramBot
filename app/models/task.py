from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: Optional[int] = None
    description: str = ""
    priority: str = "Medium"
    created_by: str = ""
    created_at: Optional[datetime] = None

    @property
    def priority_icon(self) -> str:
        return {
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(self.priority, '🟡')
