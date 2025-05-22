from sqlalchemy import select, delete
from typing import List
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.team import TeamSchema, team
from fastapi import HTTPException
from app.core.logger import logger


class TeamRepository(BaseRepository[TeamSchema]):
    def __init__(self):
        super().__init__(TeamSchema)

    async def create_team(self, db, team: team) -> team:
        team_data = team.model_dump()
        return await self.create(db, **team_data)

    async def delete_team(self, db, team_id: str) -> None:
        query = delete(self.model).where(self.model.id == team_id)
        await db.execute(query)
        await db.commit()

    async def get_all_teams(self, db) -> List[team]:
        return await self.get_all(db)
