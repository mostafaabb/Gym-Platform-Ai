# GymFlow AI - Production-Grade AI SaaS Gym Platform

## Project Overview
A complete, enterprise-level AI-powered gym operating system with real-time voice coaching, posture analysis, workout intelligence, analytics, and gym management capabilities.

## Architecture Overview

### Tech Stack (Mandatory)
- **Frontend**: Next.js 15, TypeScript, TailwindCSS, Framer Motion, Zustand, React Query, Shadcn/UI
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, WebSockets
- **AI**: OpenAI APIs, Whisper, TTS, LangChain, RAG, MediaPipe
- **DevOps**: Docker, Docker Compose, Nginx, CI/CD

### System Architecture

#### Backend Structure
```
backend/
├── main.py (FastAPI app)
├── core/
│   ├── config.py (settings)
│   ├── database.py (connections)
│   ├── security.py (JWT, bcrypt)
│   ├── exceptions.py (error handling)
│   └── rbac.py (role-based access)
├── models.py (SQLAlchemy ORM)
├── schemas/ (Pydantic DTOs)
├── api/
│   └── routes/ (60+ endpoints)
├── services/ (business logic)
├── repositories/ (data access)
├── ai/ (AI features)
├── websockets/ (real-time)
└── utils/ (helpers)
```

#### Frontend Structure
```
frontend/
├── src/
│   ├── app/ (Next.js routing)
│   ├── components/ (reusable UI)
│   ├── pages/ (feature pages)
│   ├── layouts/ (app layouts)
│   ├── hooks/ (custom hooks)
│   ├── services/ (API client)
│   ├── store/ (Zustand state)
│   ├── styles/ (TailwindCSS)
│   ├── types/ (TypeScript)
│   └── utils/ (helpers)
```

## User Roles & Permissions
1. **Super Admin**: Full system control
2. **Gym Owner**: Manage single gym
3. **Trainer**: Manage clients, classes
4. **Member**: Access AI coach, workouts

## Feature Implementation Checklist

### 1. AI Voice Coach
- Speech-to-text (Whisper)
- Text-to-speech (pyttsx3/gTTS)
- LangChain context awareness
- WebSocket streaming

### 2. Real-Time Pose Detection
- MediaPipe pose estimation
- Exercise detection algorithms
- Form correction AI
- Rep counting

### 3. Personalized Workout Generation
- AI-driven program generation
- Progressive overload tracking
- Injury prevention
- Equipment-based planning

### 4. Gym Management SaaS
- Multi-tenant isolation
- Billing & subscriptions
- Member management
- Trainer scheduling

### 5. Realtime Dashboards
- Live member tracking
- Analytics engine
- AI insights
- WebSocket updates

### 6. APIs (60+ Minimum)
- Auth endpoints
- Gym CRUD
- Member management
- Workout tracking
- Analytics
- Billing

## Database Design
- **Multi-tenant**: gym_id isolation
- **Audit logging**: all changes tracked
- **Indexing**: optimized queries
- **Relationships**: proper normalization

## Security Requirements
- JWT authentication
- Bcrypt password hashing
- Rate limiting
- CORS security
- Input validation
- SQL injection prevention
- XSS protection

## Deployment
- Docker containerization
- docker-compose orchestration
- Nginx reverse proxy
- GitHub Actions CI/CD
- Environment-based config

## Development Commands
```bash
# Backend
python -m uvicorn backend.main:app --reload

# Database
alembic upgrade head

# Frontend
npm run dev

# Docker
docker-compose up -d
```
