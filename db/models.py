from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, Boolean, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class MembershipStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    canceled = "canceled"


class WorkoutStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    gym_owner = "gym_owner"
    trainer = "trainer"
    member = "member"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    canceled = "canceled"
    expired = "expired"
    paused = "paused"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class ClassStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class NotificationType(str, enum.Enum):
    workout_reminder = "workout_reminder"
    ai_coach_message = "ai_coach_message"
    class_booking = "class_booking"
    subscription_renewal = "subscription_renewal"
    form_feedback = "form_feedback"
    achievement = "achievement"
    system = "system"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.member, nullable=False, index=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    profile_picture_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recovery_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    injury_history: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    memberships: Mapped[list[Membership]] = relationship(back_populates="user", cascade="all, delete-orphan")
    workouts: Mapped[list[Workout]] = relationship(back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[list[Conversation]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trainer_profile: Mapped[Trainer | None] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list[Notification]] = relationship(back_populates="user", cascade="all, delete-orphan")
    messages_sent: Mapped[list[Message]] = relationship(back_populates="sender", cascade="all, delete-orphan", foreign_keys="Message.sender_id")
    nutrition_logs: Mapped[list[FoodLog]] = relationship(back_populates="user", cascade="all, delete-orphan")
    meal_plans: Mapped[list[MealPlan]] = relationship(back_populates="user", cascade="all, delete-orphan")
    exercise_sessions: Mapped[list[ExerciseSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_user_role_active", "role", "is_active"),)


class Gym(Base):
    __tablename__ = "gyms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_trainers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    amenities: Mapped[dict] = mapped_column(JSON, default=dict)
    operating_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    memberships: Mapped[list[Membership]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    exercises: Mapped[list[Exercise]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    trainers: Mapped[list[Trainer]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    classes: Mapped[list[Class]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    activity_logs: Mapped[list[ActivityLog]] = relationship(back_populates="gym", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gyms.id"), nullable=False, index=True)
    status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus), default=MembershipStatus.active, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="memberships")
    gym: Mapped[Gym] = relationship(back_populates="memberships")

    __table_args__ = (Index("ix_membership_user_gym_unique", "user_id", "gym_id", unique=True),)


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gym_id: Mapped[int | None] = mapped_column(ForeignKey("gyms.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    muscle_group: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    gym: Mapped[Gym | None] = relationship(back_populates="exercises")
    workout_logs: Mapped[list[WorkoutLog]] = relationship(back_populates="exercise")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[WorkoutStatus] = mapped_column(Enum(WorkoutStatus), default=WorkoutStatus.planned, nullable=False, index=True)
    ai_plan: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="workouts")
    logs: Mapped[list[WorkoutLog]] = relationship(back_populates="workout", cascade="all, delete-orphan")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"), nullable=False, index=True)
    exercise_id: Mapped[int | None] = mapped_column(ForeignKey("exercises.id"), nullable=True, index=True)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    fatigue_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    workout: Mapped[Workout] = relationship(back_populates="logs")
    exercise: Mapped[Exercise | None] = relationship(back_populates="workout_logs")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="chat")
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    ai_message: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="conversations")


class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gyms.id"), nullable=False, index=True)
    specialization: Mapped[str] = mapped_column(String(200), nullable=False)
    certification: Mapped[str] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hourly_rate: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=50)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="trainer_profile")
    gym: Mapped[Gym] = relationship(back_populates="trainers")
    schedules: Mapped[list[TrainerSchedule]] = relationship(back_populates="trainer", cascade="all, delete-orphan")
    classes: Mapped[list[Class]] = relationship(back_populates="trainer", cascade="all, delete-orphan")


class TrainerSchedule(Base):
    __tablename__ = "trainer_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"), nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    trainer: Mapped[Trainer] = relationship(back_populates="schedules")


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gyms.id"), nullable=False, index=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    class_type: Mapped[str] = mapped_column(String(100), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ClassStatus] = mapped_column(Enum(ClassStatus), default=ClassStatus.scheduled, nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=0, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    gym: Mapped[Gym] = relationship(back_populates="classes")
    trainer: Mapped[Trainer] = relationship(back_populates="classes")
    bookings: Mapped[list[ClassBooking]] = relationship(back_populates="class_", cascade="all, delete-orphan")


class ClassBooking(Base):
    __tablename__ = "class_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    booked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="booked", nullable=False)
    attended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    class_: Mapped[Class] = relationship(back_populates="bookings")
    user: Mapped[User] = relationship()

    __table_args__ = (Index("ix_class_booking_user_class", "user_id", "class_id", unique=True),)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_monthly: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    price_yearly: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    features: Mapped[dict] = mapped_column(JSON, default=dict)
    max_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id"), nullable=False, index=True)
    gym_id: Mapped[int | None] = mapped_column(ForeignKey("gyms.id"), nullable=True, index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), default=SubscriptionStatus.active, nullable=False, index=True)
    billing_cycle: Mapped[str] = mapped_column(String(50), default="monthly", nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    renewal_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="subscriptions")
    plan: Mapped[SubscriptionPlan] = relationship(back_populates="subscriptions")
    gym: Mapped[Gym | None] = relationship(back_populates="subscriptions")
    payments: Mapped[list[PaymentTransaction]] = relationship(back_populates="subscription", cascade="all, delete-orphan")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(100), nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    subscription: Mapped[Subscription] = relationship(back_populates="payments")
    user: Mapped[User] = relationship()


class Nutrition(Base):
    __tablename__ = "nutrition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    fiber_g: Mapped[float] = mapped_column(Float, nullable=True)
    food_group: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(String(100), nullable=False)
    daily_calories: Mapped[float] = mapped_column(Float, nullable=False)
    daily_protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    daily_carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    daily_fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    meals: Mapped[dict] = mapped_column(JSON, default=dict)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="meal_plans")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    meal_plan_id: Mapped[int | None] = mapped_column(ForeignKey("meal_plans.id"), nullable=True, index=True)
    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[str] = mapped_column(String(100), nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="nutrition_logs")


class ExerciseSession(Base):
    __tablename__ = "exercise_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False, index=True)
    workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"), nullable=True, index=True)
    reps_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reps_total: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    form_quality: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="exercise_sessions")
    exercise: Mapped[Exercise] = relationship()


class FormAnalysis(Base):
    __tablename__ = "form_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exercise_session_id: Mapped[int] = mapped_column(ForeignKey("exercise_sessions.id"), nullable=False, unique=True, index=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    pose_landmarks: Mapped[dict] = mapped_column(JSON, nullable=False)
    form_score: Mapped[float] = mapped_column(Float, nullable=False)
    issues_detected: Mapped[list] = mapped_column(JSON, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, default=list)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    exercise_session: Mapped[ExerciseSession] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="notifications")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    sender: Mapped[User] = relationship(back_populates="messages_sent", foreign_keys=[sender_id])
    recipient: Mapped[User] = relationship(foreign_keys=[recipient_id])


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    gym_id: Mapped[int | None] = mapped_column(ForeignKey("gyms.id"), nullable=True, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user: Mapped[User] = relationship()
    gym: Mapped[Gym | None] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)
    changes: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="audit_logs")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gyms.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    gym: Mapped[Gym] = relationship()


Index("ix_workout_user_started", Workout.user_id, Workout.started_at.desc())
Index("ix_conversation_user_created", Conversation.user_id, Conversation.created_at.desc())
Index("ix_notification_user_read", Notification.user_id, Notification.is_read)
Index("ix_message_recipient_read", Message.recipient_id, Message.is_read)
