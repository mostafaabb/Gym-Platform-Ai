from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException
from backend.models import NutritionLog, Member
from backend.schemas import NutritionLogRequest, NutritionLogResponse
from backend.repositories.repositories import MemberRepository

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])
member_repo = MemberRepository()



@router.post("/log", response_model=NutritionLogResponse, status_code=status.HTTP_201_CREATED)
async def log_nutrition(
    member_id: int,
    request: NutritionLogRequest,
    db: AsyncSession = Depends(get_db)
):
    """Log nutrition for a member."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    nutrition_log = NutritionLog(
        member_id=member_id,
        meal_type=request.meal_type,
        food_items=request.food_items,
        total_calories=request.total_calories,
        protein_g=request.protein_g,
        carbs_g=request.carbs_g,
        fat_g=request.fat_g,
        notes=request.notes,
        logged_at=datetime.utcnow(),
    )
    db.add(nutrition_log)
    await db.commit()
    await db.refresh(nutrition_log)

    return NutritionLogResponse.model_validate(nutrition_log)


@router.get("/member/{member_id}/history")
async def get_nutrition_history(
    member_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get nutrition history for a member."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    from sqlalchemy import select
    result = await db.execute(
        select(NutritionLog)
        .where(NutritionLog.member_id == member_id)
        .order_by(NutritionLog.logged_at.desc())
        .offset(skip)
        .limit(limit)
    )
    logs = result.scalars().all()

    return {
        "member_id": member_id,
        "logs": [
            {
                "id": log.id,
                "meal_type": log.meal_type,
                "calories": log.total_calories,
                "protein": log.protein_g,
                "carbs": log.carbs_g,
                "fat": log.fat_g,
                "logged_at": log.logged_at,
            }
            for log in logs
        ]
    }


@router.post("/snap-log", response_model=NutritionLogResponse, status_code=status.HTTP_201_CREATED)
async def snap_and_log_nutrition(
    member_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Log nutrition by uploading a photo analyzed by AI Vision."""
    member = await member_repo.get(db, member_id)
    if not member:
        raise ResourceNotFoundException("Member not found")

    image_bytes = await file.read()
    
    from backend.services.ai_service import ai_service
    analysis = await ai_service.analyze_meal_image(image_bytes)

    nutrition_log = NutritionLog(
        member_id=member_id,
        meal_type=analysis.get("meal_type", "lunch"),
        food_items=analysis.get("food_items", []),
        total_calories=analysis.get("total_calories", 0.0),
        protein_g=analysis.get("protein_g", 0.0),
        carbs_g=analysis.get("carbs_g", 0.0),
        fat_g=analysis.get("fat_g", 0.0),
        notes=analysis.get("notes", ""),
        logged_at=datetime.utcnow(),
    )
    db.add(nutrition_log)
    await db.commit()
    await db.refresh(nutrition_log)

    return NutritionLogResponse.model_validate(nutrition_log)

