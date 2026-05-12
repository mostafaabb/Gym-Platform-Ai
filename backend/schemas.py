from datetime import datetime
from typing import Optional, Any
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
    total_calories: Optional[float]
    protein_g: Optional[float]
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
