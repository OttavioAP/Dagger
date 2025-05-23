from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.repository.tasks import TaskSchema, task
from app.core.repository.base_repository import BaseRepository
from fastapi import HTTPException
import uuid


class TasksRepository(BaseRepository[TaskSchema]):
    def __init__(self):
        super().__init__(TaskSchema)

    async def create_task(self, db: AsyncSession, task: task) -> task:
        db_task = TaskSchema(**task.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return task.from_orm(db_task)

    async def edit_task(
        self, db: AsyncSession, task_id: uuid.UUID, updates: dict
    ) -> task:
        result = await db.execute(
            update(TaskSchema)
            .where(TaskSchema.id == task_id)
            .values(**updates)
            .returning(TaskSchema)
        )
        db_task = result.fetchone()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        await db.commit()
        return task.from_orm(db_task)

    async def delete_task(self, db: AsyncSession, task_id: uuid.UUID):
        result = await db.execute(
            delete(TaskSchema).where(TaskSchema.id == task_id).returning(TaskSchema)
        )
        db_task = result.fetchone()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        await db.commit()
        return task.from_orm(db_task)

    async def get_by_id(self, db: AsyncSession, task_id: uuid.UUID) -> task:
        result = await db.execute(select(TaskSchema).where(TaskSchema.id == task_id))
        db_task = result.scalar_one_or_none()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.from_orm(db_task)

    async def get_all_tasks_by_team(
        self, db: AsyncSession, team_id: uuid.UUID
    ) -> list[task]:
        result = await db.execute(
            select(TaskSchema).where(TaskSchema.team_id == team_id)
        )
        db_tasks = result.scalars().all()
        return [task.from_orm(t) for t in db_tasks]

    async def get_tasks_by_ids(
        self, db: AsyncSession, task_ids: list
    ) -> list[TaskSchema]:
        if not task_ids:
            return []
        result = await db.execute(select(TaskSchema).where(TaskSchema.id.in_(task_ids)))
        return result.scalars().all()

    async def get_tasks_by_user(self, db: AsyncSession, user_id):
        from app.core.repository.user_tasks_repository import UserTasksRepository

        user_tasks_repo = UserTasksRepository()
        task_ids = await user_tasks_repo.get_task_ids_for_user(db, user_id)
        if not task_ids:
            return []
        result = await db.execute(select(TaskSchema).where(TaskSchema.id.in_(task_ids)))
        return [task.from_orm(obj) for obj in result.scalars().all()]

    async def get_completed_tasks_for_user_in_range(
        self, db: AsyncSession, user_id, start_date, end_date
    ):
        from app.core.repository.user_tasks_repository import UserTasksRepository

        user_tasks_repo = UserTasksRepository()
        task_ids = await user_tasks_repo.get_task_ids_for_user(db, user_id)
        if not task_ids:
            return []
        result = await db.execute(
            select(TaskSchema).where(
                TaskSchema.id.in_(task_ids),
                TaskSchema.date_of_completion != None,
                TaskSchema.date_of_completion >= start_date,
                TaskSchema.date_of_completion <= end_date,
            )
        )
        return [task.from_orm(obj) for obj in result.scalars().all()]

    async def get_unfinished_tasks_for_user_before(
        self, db: AsyncSession, user_id, end_date
    ):
        from app.core.repository.user_tasks_repository import UserTasksRepository

        user_tasks_repo = UserTasksRepository()
        task_ids = await user_tasks_repo.get_task_ids_for_user(db, user_id)
        if not task_ids:
            return []
        result = await db.execute(
            select(TaskSchema).where(
                TaskSchema.id.in_(task_ids),
                TaskSchema.date_of_completion == None,
                TaskSchema.deadline <= end_date,
            )
        )
        return [task.from_orm(obj) for obj in result.scalars().all()]
