from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SQLEnum, JSON, DECIMAL,
    Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.core.database import Base


class RoleEnum(str, Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    GYM_OWNER = "gym_owner"
    TRAINER = "trainer"
    MEMBER = "member"


class SubscriptionPlanEnum(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ExerciseTypeEnum(str, Enum):
    """Exercise types for classification."""
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"


class ExperienceLevelEnum(str, Enum):
    """User fitness experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class FitnessGoalEnum(str, Enum):
    """User fitness goals."""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_HEALTH = "general_health"


class PaymentStatusEnum(str, Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============== USERS ==============
class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    profile_picture_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.MEMBER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_2fa_enabled = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gym_owner_of = relationship("Gym", back_populates="owner")
    trainers = relationship("Trainer", back_populates="user", foreign_keys="Trainer.user_id")
    members = relationship("Member", back_populates="user", foreign_keys="Member.user_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    ai_sessions = relationship("AISession", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    received_notifications = relationship("NotificationLog", back_populates="recipient")
    sent_messages = relationship("Message", back_populates="sender")

    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        UniqueConstraint("email", name="uq_user_email"),
    )


# ============== GYMS ==============
class Gym(Base):
    """Gym/fitness facility model."""
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
    subscription_plan = Column(SQLEnum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.FREE)
    max_members = Column(Integer, default=100)
    max_trainers = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="gym_owner_of", foreign_keys=[owner_id])
    trainers = relationship("Trainer", back_populates="gym")
    members = relationship("Member", back_populates="gym")
    memberships = relationship("Membership", back_populates="gym")
    classes = relationship("GymClass", back_populates="gym")
    schedules = relationship("GymSchedule", back_populates="gym")
    subscriptions = relationship("Subscription", back_populates="gym")
    attendance_records = relationship("Attendance", back_populates="gym")
    reports = relationship("Report", back_populates="gym")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="gym")

    __table_args__ = (
        Index("idx_gym_owner_active", "owner_id", "is_active"),
        Index("idx_gym_slug", "slug"),
    )


# ============== TRAINERS ==============
class Trainer(Base):
    """Trainer/instructor model."""
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    bio = Column(Text, nullable=True)
    specialties = Column(JSON, default=list)  # e.g., ["strength", "cardio", "nutrition"]
    certifications = Column(JSON, default=list)
    hourly_rate = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    rating = Column(Float, default=0.0)
    total_clients = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="trainers", foreign_keys=[user_id])
    gym = relationship("Gym", back_populates="trainers")
    client_sessions = relationship("TrainingSession", back_populates="trainer")
    coaching_sessions = relationship("CoachingSession", back_populates="trainer")

    __table_args__ = (
        Index("idx_trainer_gym_active", "gym_id", "is_active"),
    )


# ============== MEMBERS ==============
class Member(Base):
    """Gym member model."""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    fitness_goal = Column(SQLEnum(FitnessGoalEnum), nullable=True)
    experience_level = Column(SQLEnum(ExperienceLevelEnum), default=ExperienceLevelEnum.BEGINNER)
    injuries = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, index=True)
    join_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="members", foreign_keys=[user_id])
    gym = relationship("Gym", back_populates="members")
    memberships = relationship("Membership", back_populates="member")
    workouts = relationship("Workout", back_populates="member")
    nutrition_logs = relationship("NutritionLog", back_populates="member")
    progress_tracking = relationship("ProgressTracking", back_populates="member")
    attendance_records = relationship("Attendance", back_populates="member")
    pose_events = relationship("PoseAnalysisEvent", back_populates="member")
    workout_plans = relationship("WorkoutPlan", back_populates="member")
    meal_plans = relationship("MealPlan", back_populates="member")

    __table_args__ = (
        Index("idx_member_gym_active", "gym_id", "is_active"),
    )


# ============== MEMBERSHIPS ==============
class Membership(Base):
    """Membership/subscription for members."""
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    subscription_plan = Column(SQLEnum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.FREE)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    auto_renew = Column(Boolean, default=True)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    member = relationship("Member", back_populates="memberships")
    gym = relationship("Gym", back_populates="memberships")

    __table_args__ = (
        Index("idx_membership_gym_active", "gym_id", "is_active"),
    )


# ============== WORKOUTS ==============
class Workout(Base):
    """Workout session record."""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    workout_type = Column(String(50), nullable=True)  # e.g., "strength", "cardio", "flexibility"
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    ai_generated = Column(Boolean, default=False)
    ai_recommendations = Column(JSON, default=dict)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout")

    __table_args__ = (
        Index("idx_workout_member_date", "member_id", "start_time"),
    )


# ============== EXERCISES ==============
class Exercise(Base):
    """Exercise library."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    exercise_type = Column(SQLEnum(ExerciseTypeEnum), nullable=False)
    muscle_groups = Column(JSON, default=list)
    instructions = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    difficulty_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")


class WorkoutExercise(Base):
    """Exercise details within a workout."""
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    form_score = Column(Float, nullable=True)  # AI posture analysis score
    completed = Column(Boolean, default=False)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")


# ============== NUTRITION ==============
class NutritionLog(Base):
    """Member nutrition tracking."""
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    meal_type = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack
    food_items = Column(JSON, default=list)
    total_calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="nutrition_logs")

    __table_args__ = (
        Index("idx_nutrition_member_date", "member_id", "logged_at"),
    )


# ============== PROGRESS TRACKING ==============
class ProgressTracking(Base):
    """Member progress and metrics."""
    __tablename__ = "progress_tracking"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    weight_kg = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    workout_count = Column(Integer, default=0)
    total_calories_burned = Column(Float, default=0)
    personal_records = Column(JSON, default=dict)  # Exercise -> weight/reps
    recovery_score = Column(Float, nullable=True)  # 0-100
    sleep_hours = Column(Float, nullable=True)
    tracked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="progress_tracking")

    __table_args__ = (
        Index("idx_progress_member_date", "member_id", "tracked_at"),
    )


# ============== TRAINING SESSIONS ==============
class TrainingSession(Base):
    """One-on-one training sessions."""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trainer = relationship("Trainer", back_populates="client_sessions")

    __table_args__ = (
        Index("idx_session_trainer_date", "trainer_id", "start_time"),
    )


# ============== GYM CLASSES ==============
class GymClass(Base):
    """Group fitness classes."""
    __tablename__ = "gym_classes"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)
    class_type = Column(String(100), nullable=True)  # yoga, crossfit, zumba, etc.
    max_capacity = Column(Integer, default=20)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=True)
    start_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    gym = relationship("Gym", back_populates="classes")
    bookings = relationship("ClassBooking", back_populates="gym_class")


# ============== GYM SCHEDULES ==============
class GymSchedule(Base):
    """Gym opening hours and schedules."""
    __tablename__ = "gym_schedules"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    day_of_week = Column(String(20), nullable=False)  # Monday-Sunday
    opening_time = Column(String(5), nullable=False)  # HH:MM
    closing_time = Column(String(5), nullable=False)
    is_closed = Column(Boolean, default=False)

    # Relationships
    gym = relationship("Gym", back_populates="schedules")


# ============== SUBSCRIPTIONS & BILLING ==============
class Subscription(Base):
    """Subscription records."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    plan = Column(SQLEnum(SubscriptionPlanEnum), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    status = Column(String(50), default="active")  # active, cancelled, past_due
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gym = relationship("Gym", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    """Payment records."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)
    stripe_payment_id = Column(String(255), nullable=True, unique=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")


# ============== SESSION SECURITY ==============
class RefreshToken(Base):
    """Refresh token rotation and session management."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    device_label = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_token_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_refresh_user_active", "user_id", "revoked_at"),
    )


# ============== AI SESSIONS ==============
class AISession(Base):
    """AI voice coach session records."""
    __tablename__ = "ai_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # voice_coach, form_analysis, etc.
    messages = Column(JSON, default=list)  # Conversation history
    metadata_json = Column("metadata", JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    ai_model = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="ai_sessions")


class CoachingSession(Base):
    """AI coaching session details."""
    __tablename__ = "coaching_sessions"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    topic = Column(String(255), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)

    # Relationships
    trainer = relationship("Trainer", back_populates="coaching_sessions")


# ============== GENERATED AI PLANS ==============
class WorkoutPlan(Base):
    """AI-generated workout plan with progression metadata."""
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    name = Column(String(255), nullable=False)
    goal = Column(String(100), nullable=False)
    weekly_structure = Column(JSON, default=dict)
    daily_workouts = Column(JSON, default=list)
    progression_strategy = Column(JSON, default=dict)
    recovery_guidance = Column(JSON, default=dict)
    source = Column(String(50), default="ai")
    created_at = Column(DateTime, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)

    member = relationship("Member", back_populates="workout_plans")

    __table_args__ = (
        Index("idx_workout_plan_member_created", "member_id", "created_at"),
    )


class MealPlan(Base):
    """AI nutrition plan with calories and macro strategy."""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    goal = Column(String(100), nullable=False)
    calories_target = Column(Integer, nullable=False)
    macro_targets = Column(JSON, default=dict)
    meals = Column(JSON, default=list)
    shopping_list = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="meal_plans")

    __table_args__ = (
        Index("idx_meal_plan_member_created", "member_id", "created_at"),
    )


# ============== ATTENDANCE, BOOKINGS & MESSAGING ==============
class Attendance(Base):
    """QR and manual attendance check-ins."""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    check_in_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    check_out_at = Column(DateTime, nullable=True)
    source = Column(String(50), default="qr")
    qr_payload = Column(String(255), nullable=True)
    metadata_json = Column("metadata", JSON, default=dict)

    gym = relationship("Gym", back_populates="attendance_records")
    member = relationship("Member", back_populates="attendance_records")

    __table_args__ = (
        Index("idx_attendance_gym_time", "gym_id", "check_in_at"),
        Index("idx_attendance_member_time", "member_id", "check_in_at"),
    )


class ClassBooking(Base):
    """Class booking records."""
    __tablename__ = "class_bookings"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("gym_classes.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    status = Column(String(50), default="booked")
    booked_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    gym_class = relationship("GymClass", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint("class_id", "member_id", name="uq_class_member_booking"),
        Index("idx_booking_member_status", "member_id", "status"),
    )


class MessageThread(Base):
    """Realtime chat thread for trainers, members, and owners."""
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=True)
    subject = Column(String(255), nullable=True)
    participant_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)

    messages = relationship("Message", back_populates="thread")

    __table_args__ = (
        Index("idx_thread_gym_last_message", "gym_id", "last_message_at"),
    )


class Message(Base):
    """Individual chat message."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")

    __table_args__ = (
        Index("idx_message_thread_created", "thread_id", "created_at"),
    )


# ============== COMPUTER VISION & ANALYTICS ==============
class PoseAnalysisEvent(Base):
    """Per-exercise form analysis events generated from pose estimation."""
    __tablename__ = "pose_analysis_events"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=True)
    ai_session_id = Column(Integer, ForeignKey("ai_sessions.id"), nullable=True)
    exercise = Column(String(100), nullable=False)
    rep_count = Column(Integer, default=0)
    form_score = Column(Float, nullable=False)
    alerts = Column(JSON, default=list)
    landmarks_summary = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="pose_events")

    __table_args__ = (
        Index("idx_pose_member_exercise_time", "member_id", "exercise", "created_at"),
    )


class AnalyticsSnapshot(Base):
    """Persisted analytics rollups for dashboards and reports."""
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    snapshot_type = Column(String(100), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    metrics = Column(JSON, default=dict)
    insights = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    gym = relationship("Gym", back_populates="analytics_snapshots")

    __table_args__ = (
        Index("idx_snapshot_gym_type_period", "gym_id", "snapshot_type", "period_start"),
        Index("idx_snapshot_member_type_period", "member_id", "snapshot_type", "period_start"),
    )


class Report(Base):
    """Generated management, retention, revenue, and AI reports."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=True)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    payload = Column(JSON, default=dict)
    status = Column(String(50), default="ready")
    created_at = Column(DateTime, default=datetime.utcnow)

    gym = relationship("Gym", back_populates="reports")

    __table_args__ = (
        Index("idx_report_gym_type_created", "gym_id", "report_type", "created_at"),
    )


# ============== AUDIT & LOGGING ==============
class AuditLog(Base):
    """Audit trail for security and compliance."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_user_action", "user_id", "action"),
    )


class NotificationLog(Base):
    """Notification and messaging log."""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=True)  # email, sms, push, in-app
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    recipient = relationship("User", back_populates="received_notifications")

    __table_args__ = (
        Index("idx_notification_recipient_read", "recipient_id", "is_read"),
    )
