from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from app.core.repository.user_repository import UserRepository
from app.services.week_service import analyze_and_create_week
from app.core.repository.week_repository import WeekRepository
from app.core.logger import logger
from app.services.database_service import DatabaseService

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.user_repository = UserRepository()
        self.week_repository = WeekRepository()
        self.db_service = DatabaseService.get_instance()

    async def process_user_week(self, user_id):
        """Process a single user's week analysis and storage."""
        try:
            # Get database session
            async with self.db_service.AsyncSessionLocal() as db:
                # Calculate week boundaries (Saturday midnight to next Saturday midnight)
                now = datetime.now()
                days_until_saturday = (5 - now.weekday()) % 7  # 5 is Saturday
                end_of_week = (now + timedelta(days=days_until_saturday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                start_of_week = end_of_week - timedelta(days=7)

                # Create and analyze the week
                week_obj = await analyze_and_create_week(db, start_of_week, end_of_week, user_id)
                
                # Encode and store the week with vector embedding
                await self.week_repository.encode_store_week(db, week_obj)
                
                logger.info(f"Successfully processed week for user {user_id}")
        except Exception as e:
            logger.error(f"Error processing week for user {user_id}: {str(e)}")

    async def process_all_users(self):
        """Process week analysis for all users."""
        try:
            # Get database session
            async with self.db_service.AsyncSessionLocal() as db:
                # Get all users
                users = await self.user_repository.get_all_users(db)
                
                # Process each user
                for user in users:
                    await self.process_user_week(user.id)
                
                logger.info("Completed weekly analysis for all users")
        except Exception as e:
            logger.error(f"Error in weekly analysis job: {str(e)}")

    def start(self):
        """Start the scheduler."""
        # Schedule the job to run every Saturday at midnight
        self.scheduler.add_job(
            self.process_all_users,
            trigger=CronTrigger(day_of_week='sat', hour=0, minute=0),
            id='weekly_analysis',
            name='Weekly User Analysis',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Weekly analysis scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Weekly analysis scheduler stopped")

# Create a singleton instance
scheduler_service = SchedulerService() 