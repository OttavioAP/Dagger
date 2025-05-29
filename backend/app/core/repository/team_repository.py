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
        try:
            logger.info(f"Creating team in repository: {team}")
            team_data = team.model_dump()
            result = await self.create(db, **team_data)
            logger.info(f"Team created in repository: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating team in repository: {e}")
            raise

    async def delete_team(self, db, team_id: str) -> None:
        try:
            logger.info(f"Deleting team in repository with id: {team_id}")
            query = delete(self.model).where(self.model.id == team_id)
            await db.execute(query)
            await db.commit()
            logger.info(f"Team deleted in repository: {team_id}")
        except Exception as e:
            logger.error(f"Error deleting team in repository: {e}")
            raise

    async def get_all_teams(self, db) -> List[team]:
        try:
            logger.info("Fetching all teams in repository")
            result = await self.get_all(db)
            logger.info(f"Fetched teams in repository: {result}")
            return result
        except Exception as e:
            logger.error(f"Error fetching teams in repository: {e}")
            raise
