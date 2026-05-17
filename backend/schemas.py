from datetime import datetime
from typing import Optional, Any, Literal
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# ============== ENUMS ==============
class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    GYM_OWNER = "gym_owner"
    TRAINER = "trainer"
    MEMBER = "member"


class SubscriptionPlanEnum(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ExperienceLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class FitnessGoalEnum(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_HEALTH = "general_health"


# ============== AUTH SCHEMAS ==============
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    role: RoleEnum = RoleEnum.MEMBER


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class EmailVerificationRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: RoleEnum
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== GYM SCHEMAS ==============
class GymCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    website: Optional[str] = None


class GymResponse(BaseModel):
    id: int
    name: str
    slug: str
    email: str
    phone: str
    address: str
    city: str
    country: str
    subscription_plan: SubscriptionPlanEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GymDetailResponse(GymResponse):
    description: Optional[str]
    max_members: int
    max_trainers: int


# ============== MEMBER SCHEMAS ==============
class MemberCreateRequest(BaseModel):
    user_id: int
    gym_id: int
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_goal: Optional[FitnessGoalEnum] = None
    experience_level: ExperienceLevelEnum = ExperienceLevelEnum.BEGINNER


class MemberResponse(BaseModel):
    id: int
    user_id: int
    gym_id: int
    age: Optional[int]
    fitness_goal: Optional[FitnessGoalEnum]
    experience_level: ExperienceLevelEnum
    is_active: bool
    join_date: datetime

    class Config:
        from_attributes = True


# ============== TRAINER SCHEMAS ==============
class TrainerCreateRequest(BaseModel):
    user_id: int
    gym_id: int
    bio: Optional[str] = None
    specialties: list[str] = []
    certifications: list[str] = []
    hourly_rate: Optional[float] = None


class TrainerResponse(BaseModel):
    id: int
    user_id: int
    gym_id: int
    specialties: list[str]
    hourly_rate: Optional[float]
    rating: float
    is_active: bool

    class Config:
        from_attributes = True


# ============== PLATFORM SCHEMAS ==============
class ClassCreateRequest(BaseModel):
    gym_id: int
    name: str
    description: Optional[str] = None
    instructor_id: Optional[int] = None
    class_type: Optional[str] = None
    max_capacity: int = Field(default=20, ge=1, le=250)
    duration_minutes: int = Field(default=45, ge=5, le=240)
    price: Optional[float] = Field(default=None, ge=0)
    start_time: datetime


class ClassBookingRequest(BaseModel):
    member_id: int


class AttendanceCheckInRequest(BaseModel):
    gym_id: int
    member_id: int
    source: Literal["qr", "manual", "kiosk", "mobile"] = "qr"
    qr_payload: Optional[str] = None


class SubscriptionCheckoutRequest(BaseModel):
    gym_id: int
    plan: SubscriptionPlanEnum
    seats: int = Field(default=1, ge=1)
    billing_cycle: Literal["monthly", "annual"] = "monthly"


class NotificationCreateRequest(BaseModel):
    recipient_id: int
    subject: Optional[str] = None
    message: str
    notification_type: Literal["email", "sms", "push", "in_app"] = "in_app"


class MessageThreadCreateRequest(BaseModel):
    gym_id: Optional[int] = None
    subject: Optional[str] = None
    participant_ids: list[int] = Field(default_factory=list)


class MessageCreateRequest(BaseModel):
    sender_id: int
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportCreateRequest(BaseModel):
    gym_id: Optional[int] = None
    generated_by_id: int
    report_type: str
    title: str
    filters: dict[str, Any] = Field(default_factory=dict)


class AnalyticsSnapshotRequest(BaseModel):
    gym_id: Optional[int] = None
    member_id: Optional[int] = None
    snapshot_type: str
    period_start: datetime
    period_end: datetime
    metrics: dict[str, Any] = Field(default_factory=dict)
    insights: list[dict[str, Any]] = Field(default_factory=list)


class PoseFrameRequest(BaseModel):
    member_id: int
    workout_id: Optional[int] = None
    exercise: Literal[
        "squat",
        "push_up",
        "bench_press",
        "deadlift",
        "pull_up",
        "lunge",
        "shoulder_press",
    ]
    landmarks: list[dict[str, float]] = Field(default_factory=list)
    frame_metadata: dict[str, Any] = Field(default_factory=dict)


class WorkoutGenerationRequest(BaseModel):
    member_id: int
    goal: FitnessGoalEnum
    weight_kg: Optional[float] = Field(default=None, ge=20, le=350)
    height_cm: Optional[float] = Field(default=None, ge=80, le=260)
    injuries: list[str] = Field(default_factory=list)
    experience_level: ExperienceLevelEnum = ExperienceLevelEnum.BEGINNER
    recovery_status: Literal["low", "moderate", "high"] = "moderate"
    available_equipment: list[str] = Field(default_factory=list)
    days_per_week: int = Field(default=4, ge=1, le=7)


class NutritionPlanRequest(BaseModel):
    member_id: int
    goal: FitnessGoalEnum
    calories_target: int = Field(default=2400, ge=900, le=8000)
    dietary_restrictions: list[str] = Field(default_factory=list)
    meals_per_day: int = Field(default=4, ge=2, le=8)


class VoiceCoachRequest(BaseModel):
    session_id: Optional[int] = None
    member_id: Optional[int] = None
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


# ============== WORKOUT SCHEMAS ==============
class WorkoutExerciseRequest(BaseModel):
    exercise_id: int
    sets: int
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None


class WorkoutCreateRequest(BaseModel):
    workout_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: int
    exercises: list[WorkoutExerciseRequest]


class WorkoutResponse(BaseModel):
    id: int
    member_id: int
    name: Optional[str]
    duration_minutes: int
    calories_burned: Optional[float]
    completed: bool
    start_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============== EXERCISE SCHEMAS ==============
class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    exercise_type: str
    difficulty_level: Optional[str]
    video_url: Optional[str]

    class Config:
        from_attributes = True


# ============== NUTRITION SCHEMAS ==============
class NutritionLogRequest(BaseModel):
    meal_type: str
    food_items: list[dict]
    total_calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None


class NutritionLogResponse(BaseModel):
    id: int
    member_id: int
    meal_type: str
    food_items: list[dict] = []
    total_calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: Optional[str] = None
    logged_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============== PROGRESS SCHEMAS ==============
class ProgressResponse(BaseModel):
    id: int
    weight_kg: Optional[float]
    body_fat_percentage: Optional[float]
    muscle_mass_kg: Optional[float]
    recovery_score: Optional[float]
    tracked_at: datetime

    class Config:
        from_attributes = True


# ============== AI SCHEMAS ==============
class AIMessageRequest(BaseModel):
    message: str
    session_type: str = "voice_coach"


class AISessionResponse(BaseModel):
    id: int
    session_type: str
    messages: list[dict] = []
    started_at: datetime
    duration_seconds: Optional[int]

    class Config:
        from_attributes = True


# ============== PAGINATION ==============
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    skip: int
    limit: int
    pages: int


# ============== ERROR RESPONSES ==============
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== ANALYTICS SCHEMAS ==============
class WorkoutStatsResponse(BaseModel):
    total_workouts: int
    total_hours: float
    total_calories: float
    average_sessions_per_week: float
    most_trained_muscle: Optional[str]


class MemberAnalyticsResponse(BaseModel):
    member_id: int
    stats: WorkoutStatsResponse
    progress: ProgressResponse
    goals: list[FitnessGoalEnum]
    last_workout: Optional[datetime]


class GymAnalyticsResponse(BaseModel):
    gym_id: int
    total_members: int
    active_members: int
    total_trainers: int
    subscription_revenue: float
    member_retention_rate: float
    peak_hours: list[dict]
