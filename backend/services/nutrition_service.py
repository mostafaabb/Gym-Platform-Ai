import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import NutritionLog, Member, MealPlan
from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class NutritionService:
    @staticmethod
    async def generate_meal_plan(
        db: AsyncSession, 
        member_id: int,
        goal: str = "weight_loss"
    ) -> MealPlan:
        """Use AI to generate a personalized meal plan."""
        member = await db.get(Member, member_id)
        if not member:
            raise ValueError("Member not found")

        # Mock AI generation - in real app, call OpenAI
        meal_plan_data = {
            "goal": goal,
            "calories_target": 2200,
            "macro_targets": {"protein": 180, "carbs": 220, "fats": 60},
            "meals": [
                {"name": "Breakfast", "items": ["Oatmeal", "Protein Shake"], "calories": 500},
                {"name": "Lunch", "items": ["Grilled Chicken", "Brown Rice"], "calories": 700},
                {"name": "Dinner", "items": ["Salmon", "Asparagus"], "calories": 600},
            ]
        }

        meal_plan = MealPlan(
            member_id=member_id,
            goal=goal,
            calories_target=meal_plan_data["calories_target"],
            macro_targets=meal_plan_data["macro_targets"],
            meals=meal_plan_data["meals"],
            created_at=datetime.utcnow()
        )
        db.add(meal_plan)
        await db.commit()
        await db.refresh(meal_plan)
        return meal_plan

    @staticmethod
    async def log_meal(
        db: AsyncSession,
        member_id: int,
        meal_type: str,
        items: List[str],
        calories: float,
        protein: float = 0,
        carbs: float = 0,
        fat: float = 0
    ) -> NutritionLog:
        """Log a consumed meal."""
        log = NutritionLog(
            member_id=member_id,
            meal_type=meal_type,
            food_items=items,
            total_calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            logged_at=datetime.utcnow()
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_daily_totals(db: AsyncSession, member_id: int, date: datetime):
        """Get total nutrients consumed on a specific day."""
        # This is a simplified version
        result = await db.execute(
            select(
                func.sum(NutritionLog.total_calories).label("calories"),
                func.sum(NutritionLog.protein_g).label("protein"),
                func.sum(NutritionLog.carbs_g).label("carbs"),
                func.sum(NutritionLog.fat_g).label("fat")
            ).where(
                NutritionLog.member_id == member_id,
                func.date(NutritionLog.logged_at) == date.date()
            )
        )
        totals = result.one()
        return {
            "calories": float(totals.calories or 0),
            "protein": float(totals.protein or 0),
            "carbs": float(totals.carbs or 0),
            "fat": float(totals.fat or 0)
        }

nutrition_service = NutritionService()
