from app.core.repository.team_repository import TeamRepository
from app.core.repository.user_repository import UserRepository
from app.core.repository.user_teams_repository import UserTeamsRepository
from app.api.teams import team_data


class UserTeamHandler:
    @staticmethod
    async def get_all_team_data(db):
        team_repo = TeamRepository()
        user_repo = UserRepository()
        user_teams_repo = UserTeamsRepository()

        teams = await team_repo.get_all_teams(db)
        users = await user_repo.get_all_users(db)
        user_teams = await user_teams_repo.get_all_user_teams(db)

        return [team_data(teams=teams, users=users, user_teams=user_teams)]
