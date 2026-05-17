from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Workout, PoseAnalysisEvent

class InjuryRiskService:
    @staticmethod
    async def calculate_member_risk(db: AsyncSession, member_id: int) -> dict:
        now = datetime.utcnow()
        
        # 1. Fetch Acute Workload (last 7 days)
        # Average calorie burn/duration times average metabolic intensity (METs)
        acute_query = select(func.sum(Workout.duration_minutes * 8.0)).where( 
            Workout.member_id == member_id,
            Workout.start_time >= now - timedelta(days=7)
        )
        acute_result = await db.execute(acute_query)
        acute_load = acute_result.scalar() or 0.0
        
        # 2. Fetch Chronic Workload (last 28 days)
        chronic_query = select(func.sum(Workout.duration_minutes * 8.0)).where(
            Workout.member_id == member_id,
            Workout.start_time >= now - timedelta(days=28)
        )
        chronic_result = await db.execute(chronic_query)
        chronic_load = (chronic_result.scalar() or 0.0) / 4.0 # Scale to weekly chronic average
        
        # 3. Calculate ACWR
        if chronic_load == 0:
            acwr = 1.0
        else:
            acwr = round(acute_load / chronic_load, 2)
            
        # 4. Pull recent form compliance
        form_query = select(func.avg(PoseAnalysisEvent.form_score)).where(
            PoseAnalysisEvent.member_id == member_id,
            PoseAnalysisEvent.created_at >= now - timedelta(days=7)
        )
        form_result = await db.execute(form_query)
        avg_form_score = form_result.scalar() or 100.0
        
        # 5. Determine risk level
        risk_level = "low"
        risk_factors = []
        recommendations = ["Keep training consistently within your parameters."]
        
        if acwr > 1.5:
            risk_level = "high"
            risk_factors.append("Spike in weekly workload (ACWR > 1.5)")
            recommendations.append("Reduce training volume by 20% next week to allow tissue repair.")
        elif acwr < 0.8:
            risk_level = "moderate"
            risk_factors.append("Low training baseline (Conditioning drop)")
            recommendations.append("Steadily progress workouts to avoid acute strains.")
            
        if avg_form_score < 75.0:
            risk_level = "high"
            risk_factors.append(f"Suboptimal movement mechanics (Average Form Score: {round(avg_form_score, 1)}%)")
            recommendations.append("Book an AI form-review coaching session targeting your lowest scores.")
            
        return {
            "member_id": member_id,
            "acwr": acwr,
            "injury_risk_score": round(max(0.0, min(100.0, (acwr * 30) + (100 - avg_form_score))), 1),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations
        }
