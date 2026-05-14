from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.exceptions import ResourceNotFoundException, ValidationException
from backend.models import Gym, Member
from backend.schemas import GymCreateRequest, GymResponse, GymDetailResponse, MemberCreateRequest, MemberResponse
from backend.repositories.repositories import GymRepository, MemberRepository

router = APIRouter(prefix="/gyms", tags=["Gyms"])
gym_repo = GymRepository()
member_repo = MemberRepository()


@router.post("", response_model=GymDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_gym(request: GymCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new gym."""
    import re
    import unicodedata

    slug = unicodedata.normalize("NFKD", request.name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower() or "gym"

    gym = Gym(
        name=request.name,
        slug=slug,
        description=request.description,
        email=request.email,
        phone=request.phone,
        address=request.address,
        city=request.city,
        state=request.state,
        country=request.country,
        postal_code=request.postal_code,
        website=request.website,
        owner_id=1,  # TODO: Get from auth context
    )
    db.add(gym)
    await db.commit()
    await db.refresh(gym)

    return GymDetailResponse.model_validate(gym)


@router.get("/{gym_id}", response_model=GymDetailResponse)
async def get_gym(gym_id: int, db: AsyncSession = Depends(get_db)):
    """Get gym details."""
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")

    return GymDetailResponse.model_validate(gym)


@router.get("", response_model=list[GymResponse])
async def list_gyms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all active gyms with pagination."""
    gyms, _ = await gym_repo.get_all(db, skip=skip, limit=limit, filters={"is_active": True})
    return [GymResponse.model_validate(g) for g in gyms]


@router.put("/{gym_id}", response_model=GymDetailResponse)
async def update_gym(gym_id: int, request: GymCreateRequest, db: AsyncSession = Depends(get_db)):
    """Update gym details."""
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(gym, key, value)

    db.add(gym)
    await db.commit()
    await db.refresh(gym)

    return GymDetailResponse.model_validate(gym)


@router.delete("/{gym_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gym(gym_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a gym."""
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")

    gym.is_active = False
    db.add(gym)
    await db.commit()


@router.post("/{gym_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member_to_gym(gym_id: int, request: MemberCreateRequest, db: AsyncSession = Depends(get_db)):
    """Add a member to a gym."""
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")

    # Check if member already exists in this gym
    existing = await member_repo.get_by_user_and_gym(db, request.user_id, gym_id)
    if existing:
        raise ValidationException("Member already exists in this gym")

    member = Member(
        user_id=request.user_id,
        gym_id=gym_id,
        age=request.age,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        fitness_goal=request.fitness_goal,
        experience_level=request.experience_level,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    return MemberResponse.model_validate(member)


@router.get("/{gym_id}/members", response_model=list[MemberResponse])
async def get_gym_members(
    gym_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all members of a gym."""
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")

    members = await member_repo.get_gym_members(db, gym_id)
    return [MemberResponse.model_validate(m) for m in members[skip:skip+limit]]


@router.get("/{gym_id}/analytics", tags=["Analytics"])
async def get_gym_analytics(gym_id: int, db: AsyncSession = Depends(get_db)):
    """Get business analytics for a gym."""
    from backend.services.gym_service import gym_service
    
    gym = await gym_repo.get(db, gym_id)
    if not gym:
        raise ResourceNotFoundException("Gym not found")
        
    analytics = await gym_service.get_gym_analytics(db, gym_id)
    return analytics
