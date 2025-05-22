from sqlalchemy import select, delete
from typing import List
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.user_teams import UserTeamsSchema, user_teams
from fastapi import HTTPException
from app.core.logger import logger


class UserTeamsRepository(BaseRepository[UserTeamsSchema]):
    def __init__(self):
        super().__init__(UserTeamsSchema)

    async def add_user_team(self, db, user_team: user_teams) -> user_teams:
        user_team_data = user_team.model_dump()
        return await self.create(db, **user_team_data)

    async def delete_user_team(self, db, user_id: str, team_id: str) -> None:
        query = delete(self.model).where(
            self.model.user_id == user_id, self.model.team_id == team_id
        )
        await db.execute(query)
        await db.commit()

    async def get_all_user_teams(self, db) -> List[user_teams]:
        return await self.get_all(db)
