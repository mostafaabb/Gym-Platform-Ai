from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.core.database import get_db
from backend.models import Member, User

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("")
async def get_leaderboard(
    gym_id: int = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get the gym leaderboard ranked by consistency score."""
    query = select(Member, User).join(User, Member.user_id == User.id)
    
    if gym_id:
        query = query.where(Member.gym_id == gym_id)
        
    query = query.order_by(desc(Member.consistency_score)).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    leaderboard = []
    for i, (member, user) in enumerate(rows):
        leaderboard.append({
            "rank": i + 1,
            "user_id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "avatar": user.profile_picture_url,
            "score": member.consistency_score,
            "avg_form": member.form_score_avg,
            "role": user.role
        })
        
    return leaderboard
