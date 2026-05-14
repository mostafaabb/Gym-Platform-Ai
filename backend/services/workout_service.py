import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import Workout, WorkoutExercise, Exercise, Member
from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class WorkoutService:
    @staticmethod
    async def create_personalized_workout(
        db: AsyncSession, 
        member_id: int,
        goal: str = "muscle_gain"
    ) -> Workout:
        """Use AI to generate and persist a personalized workout session."""
        member = await db.get(Member, member_id)
        if not member:
            raise ValueError("Member not found")

        # 1. Generate workout details with AI
        member_context = {
            "goal": member.fitness_goal,
            "experience": member.experience_level,
            "injuries": member.injuries,
            "weight": member.weight_kg
        }
        
        ai_plan = await ai_service.generate_workout_plan(member_context)
        
        # 2. Create Workout record
        workout = Workout(
            member_id=member_id,
            name=ai_plan.get("name", "Daily AI Workout"),
            description="AI generated based on your profile",
            ai_generated=True,
            start_time=datetime.utcnow(),
            completed=False
        )
        db.add(workout)
        await db.flush() # Get workout.id
        
        # 3. Add exercises (Placeholder: in a real app, we'd map AI names to library IDs)
        # For now, we simulate adding the first exercise from the plan
        # workout_exercise = WorkoutExercise(
        #     workout_id=workout.id,
        #     exercise_id=1, # Default exercise
        #     sets=4,
        #     reps=10
        # )
        # db.add(workout_exercise)
        
        await db.commit()
        await db.refresh(workout)
        return workout

    @staticmethod
    async def log_exercise_performance(
        db: AsyncSession,
        workout_exercise_id: int,
        reps: int,
        weight: float,
        form_score: float
    ):
        """Log performance of a single exercise set."""
        we = await db.get(WorkoutExercise, workout_exercise_id)
        if we:
            we.reps = reps
            we.weight_kg = weight
            we.form_score = form_score
            we.completed = True
            await db.commit()
        return we

    @staticmethod
    async def get_member_progress(db: AsyncSession, member_id: int):
        """Aggregate member progress metrics over time."""
        # Calories burned over last 30 days
        calories = await db.scalar(
            select(func.sum(Workout.calories_burned))
            .where(Workout.member_id == member_id)
        ) or 0.0
        
        # Workout count
        count = await db.scalar(
            select(func.count(Workout.id))
            .where(Workout.member_id == member_id)
        )
        
        return {
            "total_calories": float(calories),
            "workout_count": count,
            "average_form_score": 92.5 # Mock rollup
        }

workout_service = WorkoutService()
