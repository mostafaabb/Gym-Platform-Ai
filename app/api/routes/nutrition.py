from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_current_user
from db.models import MealPlan, FoodLog, User

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


class FoodLogCreate(BaseModel):
    food_name: str
    quantity: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    meal_plan_id: int | None = None


class FoodLogResponse(BaseModel):
    id: int
    food_name: str
    quantity: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    logged_at: datetime

    class Config:
        from_attributes = True


class MealPlanCreate(BaseModel):
    name: str
    goal: str
    daily_calories: float
    daily_protein_g: float
    daily_carbs_g: float
    daily_fat_g: float
    meals: dict | None = None
    end_date: datetime | None = None


class MealPlanResponse(BaseModel):
    id: int
    name: str
    goal: str
    daily_calories: float
    daily_protein_g: float
    daily_carbs_g: float
    daily_fat_g: float
    meals: dict
    start_date: datetime
    end_date: datetime | None
    is_active: bool

    class Config:
        from_attributes = True


class NutritionStats(BaseModel):
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    goal_calories: float
    calories_remaining: float


@router.post("/log-food", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_food(
    request: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log food intake"""
    food_log = FoodLog(
        user_id=current_user.id,
        meal_plan_id=request.meal_plan_id,
        food_name=request.food_name,
        quantity=request.quantity,
        calories=request.calories,
        protein_g=request.protein_g,
        carbs_g=request.carbs_g,
        fat_g=request.fat_g,
    )
    db.add(food_log)
    db.commit()
    db.refresh(food_log)
    return FoodLogResponse.from_orm(food_log)


@router.get("/logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user food logs"""
    logs = db.query(FoodLog).filter(FoodLog.user_id == current_user.id).offset(skip).limit(limit).all()
    return [FoodLogResponse.from_orm(l) for l in logs]


@router.post("/meal-plan", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    request: MealPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create meal plan"""
    meal_plan = MealPlan(
        user_id=current_user.id,
        name=request.name,
        goal=request.goal,
        daily_calories=request.daily_calories,
        daily_protein_g=request.daily_protein_g,
        daily_carbs_g=request.daily_carbs_g,
        daily_fat_g=request.daily_fat_g,
        meals=request.meals or {},
        end_date=request.end_date,
        is_active=True,
    )
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)
    return MealPlanResponse.from_orm(meal_plan)


@router.get("/meal-plans", response_model=list[MealPlanResponse])
async def get_meal_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user meal plans"""
    plans = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).offset(skip).limit(limit).all()
    return [MealPlanResponse.from_orm(p) for p in plans]


@router.get("/stats", response_model=NutritionStats)
async def get_nutrition_stats(
    date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get nutrition statistics for date"""
    from datetime import datetime, timedelta

    if date:
        target_date = datetime.fromisoformat(date)
    else:
        target_date = datetime.utcnow()

    start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start,
        FoodLog.logged_at < end
    ).all()

    total_calories = sum(l.calories for l in logs)
    total_protein = sum(l.protein_g for l in logs)
    total_carbs = sum(l.carbs_g for l in logs)
    total_fat = sum(l.fat_g for l in logs)

    active_plan = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id,
        MealPlan.is_active == True
    ).first()

    goal_calories = active_plan.daily_calories if active_plan else 2000.0
    calories_remaining = goal_calories - total_calories

    return NutritionStats(
        date=target_date.date().isoformat(),
        total_calories=total_calories,
        total_protein_g=total_protein,
        total_carbs_g=total_carbs,
        total_fat_g=total_fat,
        goal_calories=goal_calories,
        calories_remaining=calories_remaining,
    )
