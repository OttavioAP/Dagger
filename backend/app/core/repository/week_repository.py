from sqlalchemy import select, and_, func, text
from typing import List, Optional, Tuple
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.week import WeekSchema, week
from app.schema.repository.user import UserSchema
from app.schema.repository.team import TeamSchema
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from pgvector.sqlalchemy import Vector
import uuid
from app.core.logger import logger
from app.services.llm_service import LLMService


class WeekRepository(BaseRepository[WeekSchema]):
    def __init__(self):
        super().__init__(WeekSchema)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    async def get_by_id(self, db, week_id: uuid.UUID) -> week:
        try:
            result = await db.execute(
                select(self.model).where(self.model.id == week_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=404, detail="Week not found")
            return week.from_orm(obj)
        except Exception as e:
            logger.exception(f"Exception in get_by_id: {e}")
            raise

    async def non_semantic_week_search(
        self,
        db,
        number_of_weeks: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        collaborators: Optional[List[uuid.UUID]] = None,
        missed_deadlines_range: Optional[Tuple[int, int]] = None,
        completed_task_range: Optional[Tuple[int, int]] = None,
        points_range: Optional[Tuple[int, int]] = None,
    ) -> List[week]:
        try:
            # Build the base query
            base_query = select(self.model)

            # Add metadata filters
            if start_date:
                base_query = base_query.where(self.model.start_date >= start_date)
            if end_date:
                base_query = base_query.where(self.model.end_date <= end_date)
            if user_id:
                base_query = base_query.where(self.model.user_id == user_id)
            if team_id:
                # Join with users table to filter by team
                base_query = base_query.join(
                    UserSchema, self.model.user_id == UserSchema.id
                ).where(UserSchema.team_id == team_id)
            if collaborators:
                base_query = base_query.where(
                    self.model.collaborators.overlap(collaborators)
                )
            if missed_deadlines_range:
                min_missed, max_missed = missed_deadlines_range
                base_query = base_query.where(
                    func.array_length(self.model.missed_deadlines, 1).between(
                        min_missed, max_missed
                    )
                )
            if completed_task_range:
                min_completed, max_completed = completed_task_range
                base_query = base_query.where(
                    func.array_length(self.model.completed_tasks, 1).between(
                        min_completed, max_completed
                    )
                )
            if points_range:
                min_points, max_points = points_range
                base_query = base_query.where(
                    self.model.points_completed.between(min_points, max_points)
                )

            # Order by start_date descending and limit results
            base_query = base_query.order_by(self.model.start_date.desc()).limit(
                number_of_weeks
            )

            result = await db.execute(base_query)
            return [week.from_orm(obj) for obj in result.scalars().all()]
        except Exception as e:
            logger.exception(f"Exception in non_semantic_week_search: {e}")
            raise

    async def get_weeks(
        self, db, user_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> List[week]:
        try:
            query = select(self.model)
            if user_id:
                query = query.where(self.model.user_id == user_id)
            elif team_id:
                # Join users to week, filter by team_id
                query = query.join(
                    UserSchema, self.model.user_id == UserSchema.id
                ).where(UserSchema.team_id == team_id)
            result = await db.execute(query)
            return [week.from_orm(obj) for obj in result.scalars().all()]
        except Exception as e:
            logger.exception(f"Exception in get_weeks: {e}")
            raise

    async def create_week(self, db, week_obj: week) -> week:
        try:
            week_data = week_obj.model_dump()
            db_week = WeekSchema(**week_data)
            db.add(db_week)
            await db.commit()
            await db.refresh(db_week)
            return week.from_orm(db_week)
        except Exception as e:
            logger.exception(f"Exception in create_week: {e}")
            raise

    async def store_week(self, db, week_and_vector: tuple[week, list[float]]):
        """
        Store a week and its 1024-dim vector embedding in the database.
        """
        try:
            week_obj, embedding = week_and_vector
            week_data = week_obj.model_dump()
            week_data["embedding"] = embedding
            db_week = WeekSchema(**week_data)
            db.add(db_week)
            await db.commit()
            await db.refresh(db_week)
            return week.from_orm(db_week)
        except Exception as e:
            logger.exception(f"Exception in store_week: {e}")
            raise

    async def search_weeks(
        self,
        db,
        query: str,
        number_of_weeks: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[uuid.UUID] = None,
        collaborators: Optional[List[uuid.UUID]] = None,
        missed_deadlines_range: Optional[Tuple[int, int]] = None,
        completed_task_range: Optional[Tuple[int, int]] = None,
        points_range: Optional[Tuple[int, int]] = None,
    ) -> List[week]:
        """Search weeks using semantic search and metadata filters."""
        try:
            query_embedding = self.model.encode(query)

            # Build the base query
            base_query = select(self.model)

            # Add metadata filters
            if start_date:
                base_query = base_query.where(self.model.start_date >= start_date)
            if end_date:
                base_query = base_query.where(self.model.end_date <= end_date)
            if user_id:
                base_query = base_query.where(self.model.user_id == user_id)
            if collaborators:
                base_query = base_query.where(
                    self.model.collaborators.overlap(collaborators)
                )
            if missed_deadlines_range:
                min_missed, max_missed = missed_deadlines_range
                base_query = base_query.where(
                    func.array_length(self.model.missed_deadlines, 1).between(
                        min_missed, max_missed
                    )
                )
            if completed_task_range:
                min_completed, max_completed = completed_task_range
                base_query = base_query.where(
                    func.array_length(self.model.completed_tasks, 1).between(
                        min_completed, max_completed
                    )
                )
            if points_range:
                min_points, max_points = points_range
                base_query = base_query.where(
                    self.model.points_completed.between(min_points, max_points)
                )

            # Add vector similarity search
            base_query = base_query.order_by(
                self.model.embedding.cosine_distance(query_embedding)
            ).limit(number_of_weeks)

            result = await db.execute(base_query)
            return [week.from_orm(obj) for obj in result.scalars().all()]
        except Exception as e:
            logger.exception(f"Exception in search_weeks: {e}")
            raise

    async def compare_weeks(
        self,
        db,
        vector: np.ndarray,
        number_of_weeks: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[uuid.UUID] = None,
        collaborators: Optional[List[uuid.UUID]] = None,
        missed_deadlines_range: Optional[Tuple[int, int]] = None,
        completed_task_range: Optional[Tuple[int, int]] = None,
        points_range: Optional[Tuple[int, int]] = None,
    ) -> List[week]:
        """Find similar weeks using vector similarity and metadata filters."""
        try:
            # Build the base query
            base_query = select(self.model)

            # Add metadata filters
            if start_date:
                base_query = base_query.where(self.model.start_date >= start_date)
            if end_date:
                base_query = base_query.where(self.model.end_date <= end_date)
            if user_id:
                base_query = base_query.where(self.model.user_id == user_id)
            if collaborators:
                base_query = base_query.where(
                    self.model.collaborators.overlap(collaborators)
                )
            if missed_deadlines_range:
                min_missed, max_missed = missed_deadlines_range
                base_query = base_query.where(
                    func.array_length(self.model.missed_deadlines, 1).between(
                        min_missed, max_missed
                    )
                )
            if completed_task_range:
                min_completed, max_completed = completed_task_range
                base_query = base_query.where(
                    func.array_length(self.model.completed_tasks, 1).between(
                        min_completed, max_completed
                    )
                )
            if points_range:
                min_points, max_points = points_range
                base_query = base_query.where(
                    self.model.points_completed.between(min_points, max_points)
                )

            # Add vector similarity search
            base_query = base_query.order_by(
                self.model.embedding.cosine_distance(vector)
            ).limit(number_of_weeks)

            result = await db.execute(base_query)
            return [week.from_orm(obj) for obj in result.scalars().all()]
        except Exception as e:
            logger.exception(f"Exception in compare_weeks: {e}")
            raise
