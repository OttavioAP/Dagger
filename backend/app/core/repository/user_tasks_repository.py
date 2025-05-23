from sqlalchemy import select
from typing import List
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.user_tasks import UserTasksSchema, user_tasks
from fastapi import HTTPException
from app.core.logger import logger


class UserTasksRepository(BaseRepository[UserTasksSchema]):
    def __init__(self):
        super().__init__(UserTasksSchema)

    async def add_user_task(self, db, user_task: user_tasks) -> user_tasks:
        user_task_data = user_task.model_dump()
        return await self.create(db, **user_task_data)

    async def delete_user_task(self, db, user_id: str, task_id: str) -> None:
        await self.delete(db, user_id, task_id)

    async def get_all_user_tasks(self, db) -> List[user_tasks]:
        return await self.get_all(db)

    async def get_task_ids_for_user(self, db, user_id):
        result = await db.execute(
            select(UserTasksSchema.task_id).where(UserTasksSchema.user_id == user_id)
        )
        return [row[0] for row in result.fetchall()]

    async def get_user_ids_for_task(self, db, task_id):
        result = await db.execute(
            select(UserTasksSchema.user_id).where(UserTasksSchema.task_id == task_id)
        )
        return [row[0] for row in result.fetchall()]
