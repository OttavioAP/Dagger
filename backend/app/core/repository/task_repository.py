from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.repository.tasks import TaskSchema, task, TaskPriority, TaskFocus
from app.core.repository.base_repository import BaseRepository
from fastapi import HTTPException
import uuid
from datetime import datetime
from app.core.logger import logger


class TasksRepository(BaseRepository[TaskSchema]):
    def __init__(self):
        super().__init__(TaskSchema)

    async def create_task(self, db: AsyncSession, task_data: dict) -> task:
        try:
            logger.info(f"Creating task with data: {task_data}")
            # Remove setting date_of_creation; let DB handle default
            if "date_of_creation" in task_data:
                del task_data["date_of_creation"]

            # Ensure priority and focus are set to defaults if not provided
            if "priority" not in task_data:
                task_data["priority"] = TaskPriority.LOW
            if "focus" not in task_data:
                task_data["focus"] = TaskFocus.LOW

            db_task = TaskSchema(**task_data)
            db.add(db_task)
            await db.commit()
            await db.refresh(db_task)
            logger.info(f"Task created: {db_task}")
            return task.from_orm(db_task)
        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error creating task: {e}")

    async def edit_task(
        self, db: AsyncSession, task_id: uuid.UUID, updates: dict
    ) -> task:
        try:
            logger.info(f"Editing task {task_id} with updates: {updates}")
            # Remove None values from updates
            updates = {k: v for k, v in updates.items() if v is not None}

            if not updates:
                # If no valid updates, return current task
                return await self.get_by_id(db, task_id)

            # First check if task exists
            existing_task = await self.get_by_id(db, task_id)
            if not existing_task:
                raise HTTPException(status_code=404, detail="Task not found")

            # Update the task
            result = await db.execute(
                update(TaskSchema)
                .where(TaskSchema.id == task_id)
                .values(**updates)
                .returning(TaskSchema)
            )
            updated_task = result.scalar_one_or_none()
            if not updated_task:
                raise HTTPException(status_code=404, detail="Task not found")

            await db.commit()
            logger.info(f"Task updated: {updated_task}")
            return task.from_orm(updated_task)
        except Exception as e:
            logger.error(f"Error editing task {task_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error editing task: {e}")

    async def delete_task(self, db: AsyncSession, task_id: uuid.UUID):
        try:
            logger.info(f"Deleting task {task_id}")
            result = await db.execute(
                delete(TaskSchema).where(TaskSchema.id == task_id).returning(TaskSchema)
            )
            db_task = result.fetchone()
            if not db_task:
                raise HTTPException(status_code=404, detail="Task not found")
            await db.commit()
            logger.info(f"Task deleted: {db_task}")
            return task.from_orm(db_task)
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error deleting task: {e}")

    async def get_by_id(self, db: AsyncSession, task_id: uuid.UUID) -> task:
        try:
            logger.info(f"Getting task by id: {task_id}")
            result = await db.execute(
                select(TaskSchema).where(TaskSchema.id == task_id)
            )
            db_task = result.scalar_one_or_none()
            if not db_task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task.from_orm(db_task)
        except Exception as e:
            logger.error(f"Error getting task by id {task_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error getting task by id: {e}"
            )

    async def get_tasks_by_ids(
        self, db: AsyncSession, task_ids: list
    ) -> list[TaskSchema]:
        try:
            logger.info(f"Getting tasks by ids: {task_ids}")
            if not task_ids:
                return []
            result = await db.execute(
                select(TaskSchema).where(TaskSchema.id.in_(task_ids))
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting tasks by ids {task_ids}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error getting tasks by ids: {e}"
            )

    async def get_tasks_by_user(self, db: AsyncSession, user_id):
        try:
            logger.info(f"Getting tasks for user: {user_id}")
            from app.core.repository.user_tasks_repository import UserTasksRepository

            user_tasks_repo = UserTasksRepository()
            task_ids = await user_tasks_repo.get_task_ids_for_user(db, user_id)
            if not task_ids:
                return []
            result = await db.execute(
                select(TaskSchema).where(TaskSchema.id.in_(task_ids))
            )
            return [task.from_orm(obj) for obj in result.scalars().all()]
        except Exception as e:
            logger.error(f"Error getting tasks for user {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error getting tasks for user: {e}"
            )

    async def get_completed_tasks_for_user_in_range(
        self, db: AsyncSession, user_id, start_date, end_date
    ):
        try:
            logger.info(
                f"Getting completed tasks for user {user_id} in range {start_date} to {end_date}"
            )
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
        except Exception as e:
            logger.error(
                f"Error getting completed tasks for user {user_id} in range: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error getting completed tasks for user in range: {e}",
            )

    async def get_unfinished_tasks_for_user_before(
        self, db: AsyncSession, user_id, end_date
    ):
        try:
            logger.info(
                f"Getting unfinished tasks for user {user_id} before {end_date}"
            )
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
        except Exception as e:
            logger.error(
                f"Error getting unfinished tasks for user {user_id} before {end_date}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error getting unfinished tasks for user before: {e}",
            )
