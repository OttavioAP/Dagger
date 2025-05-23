from sqlalchemy import select, update
from typing import List
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.user import UserSchema, user
from fastapi import HTTPException
from app.core.logger import logger


class UserRepository(BaseRepository[UserSchema]):
    def __init__(self):
        super().__init__(UserSchema)

    async def create_user(self, db, user: user) -> user:
        user_data = user.model_dump()
        logger.info(f"Creating user: {user_data}")
        return await self.create(db, **user_data)

    async def get_by_username(self, db, username: str) -> user | None:
        try:
            query = select(self.model).where(self.model.username == username)
            result = await db.execute(query)
            user_obj = result.scalar_one_or_none()
            logger.info(f"User found: {user_obj}")
            return user_obj
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            raise HTTPException(status_code=404, message=str(e))

    async def get_user(self, db, id: str) -> user:
        id_value = self._convert_id(id)
        query = select(self.model).where(self.model.id == id_value)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, db, user: user) -> user:
        # Convert the user data, excluding None values
        user_data = {
            k: v
            for k, v in user.model_dump().items()
            if v is not None and k != "id"  # Exclude id from update
        }

        query = (
            update(self.model)
            .where(self.model.id == user.id)  # Use id instead of user_id
            .values(**user_data)
            .returning(self.model)
        )

        result = await db.execute(query)
        await db.commit()

        updated_user = result.scalar_one_or_none()
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return updated_user

    async def delete_user(self, db, user_id: str) -> user:
        return await self.delete(db, id=user_id)

    async def get_all_users(self, db) -> List[user]:
        return await self.get_all(db)

    async def get_users_by_team(self, db, team_id: str):
        query = select(self.model).where(self.model.team_id == team_id)
        result = await db.execute(query)
        return result.scalars().all()
