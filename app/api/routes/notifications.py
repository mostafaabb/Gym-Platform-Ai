from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, get_current_user
from db.models import Notification, User, NotificationType

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    message: str
    metadata: dict | None = None


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user notifications"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return [NotificationResponse.from_orm(n) for n in notifications]


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't mark this notification")

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()

    return {"message": "Notification marked as read"}


@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})

    db.commit()
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete this notification")

    db.delete(notification)
    db.commit()


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get unread notification count"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}
