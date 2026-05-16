import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models import Member, Achievement, MemberAchievement, Workout

logger = logging.getLogger(__name__)

class GamificationService:
    async def process_workout_completion(self, db: AsyncSession, member_id: int, workout: Workout):
        """Award points and check for achievements after a workout."""
        points = 50
        if workout.calories_burned and workout.calories_burned > 500:
            points += 20
            
        await db.execute(
            update(Member)
            .where(Member.id == member_id)
            .values(
                consistency_score=Member.consistency_score + points,
                form_score_avg=(Member.form_score_avg * 0.8) + ((workout.form_score or 90) * 0.2)
            )
        )
        
        await self._check_achievements(db, member_id)
        await db.commit()

    async def _check_achievements(self, db: AsyncSession, member_id: int):
        result = await db.execute(select(Member).where(Member.id == member_id))
        member = result.scalars().first()
        if not member: return

        if member.consistency_score >= 50:
            await self._award_achievement(db, member_id, "First Step")
        if member.consistency_score >= 1000:
            await self._award_achievement(db, member_id, "Consistency King")

    async def _award_achievement(self, db: AsyncSession, member_id: int, achievement_name: str):
        result = await db.execute(select(Achievement).where(Achievement.name == achievement_name))
        achievement = result.scalars().first()
        
        if not achievement:
            achievement = Achievement(name=achievement_name, description=f"Unlocked {achievement_name}!", category="general")
            db.add(achievement)
            await db.flush()

        exists = await db.execute(select(MemberAchievement).where((MemberAchievement.member_id == member_id) & (MemberAchievement.achievement_id == achievement.id)))
        if not exists.scalars().first():
            new_earned = MemberAchievement(member_id=member_id, achievement_id=achievement.id)
            db.add(new_earned)
            logger.info(f"Member {member_id} earned achievement: {achievement_name}")

gamification_service = GamificationService()
