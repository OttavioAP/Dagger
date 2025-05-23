from sqlalchemy import select, and_
from typing import List, Optional
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.week import WeekSchema, week
from app.schema.repository.user import UserSchema
from app.schema.repository.team import TeamSchema
from fastapi import HTTPException


class WeekRepository(BaseRepository[WeekSchema]):
    def __init__(self):
        super().__init__(WeekSchema)

    async def get_weeks(
        self, db, user_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> List[week]:
        query = select(self.model)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        elif team_id:
            # Join users to week, filter by team_id
            query = query.join(UserSchema, self.model.user_id == UserSchema.id).where(
                UserSchema.team_id == team_id
            )
        result = await db.execute(query)
        return [week.from_orm(obj) for obj in result.scalars().all()]

    async def create_week(self, db, week_obj: week) -> week:
        week_data = week_obj.model_dump()
        db_week = WeekSchema(**week_data)
        db.add(db_week)
        await db.commit()
        await db.refresh(db_week)
        return week.from_orm(db_week)
