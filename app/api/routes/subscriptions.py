from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.api.deps import get_db, get_current_user
from db.models import Subscription, SubscriptionPlan, User, SubscriptionStatus

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionPlanResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price_monthly: Decimal
    price_yearly: Decimal
    features: dict
    max_members: int | None
    is_active: bool

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    billing_cycle: str
    start_date: datetime
    end_date: datetime | None
    renewal_date: datetime | None
    auto_renew: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan_id: int
    gym_id: int | None = None
    billing_cycle: str = "monthly"
    auto_renew: bool = True


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def get_subscription_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscription plans"""
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).offset(skip).limit(limit).all()
    return [SubscriptionPlanResponse.from_orm(p) for p in plans]


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscription plan"""
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    return SubscriptionPlanResponse.from_orm(plan)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create subscription"""
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == request.plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == SubscriptionStatus.active
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has active subscription")

    from datetime import timedelta
    if request.billing_cycle == "yearly":
        end_date = datetime.utcnow() + timedelta(days=365)
    else:
        end_date = datetime.utcnow() + timedelta(days=30)

    subscription = Subscription(
        user_id=current_user.id,
        plan_id=request.plan_id,
        gym_id=request.gym_id,
        status=SubscriptionStatus.active,
        billing_cycle=request.billing_cycle,
        start_date=datetime.utcnow(),
        end_date=end_date,
        renewal_date=end_date,
        auto_renew=request.auto_renew,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return SubscriptionResponse.from_orm(subscription)


@router.get("/me", response_model=SubscriptionResponse | None)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == SubscriptionStatus.active
    ).first()

    if not subscription:
        return None

    return SubscriptionResponse.from_orm(subscription)


@router.post("/{subscription_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    if subscription.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't cancel this subscription")

    subscription.status = SubscriptionStatus.canceled
    db.commit()
    return {"message": "Subscription canceled"}
