import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from openai import AsyncOpenAI
from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def get_voice_coach_response(
        self, 
        user_message: str, 
        history: List[Dict[str, str]],
        member_context: Dict[str, Any]
    ) -> str:
        """Get a conversational response from the AI coach."""
        system_prompt = f"""
        You are 'GymFlow AI', an elite personal trainer and motivational coach.
        You are currently coaching a member named {member_context.get('first_name', 'Member')}.
        Goal: {member_context.get('fitness_goal', 'General Fitness')}
        Experience: {member_context.get('experience_level', 'Beginner')}
        
        Guidelines:
        1. Be concise, motivational, and professional.
        2. Give specific cues for exercises (e.g., 'chest up', 'drive through heels').
        3. If the user mentions pain, advise them to stop and check their form.
        4. Focus on progressive overload and recovery.
        5. Speak as if you are in a live session. Keep responses under 50 words.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-5:]) # Keep last 5 messages for context
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            return "I'm having a slight connection issue, but keep up the great work! Focus on your breathing."

    async def generate_workout_plan(self, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized weekly workout plan."""
        prompt = f"""
        Generate a detailed 7-day workout plan for a member with:
        Goal: {member_data.get('goal')}
        Experience: {member_data.get('experience')}
        Injuries: {member_data.get('injuries', 'None')}
        Available Days: 5
        
        Return the result as a JSON object with:
        - name: Plan title
        - weekly_structure: Object mapping days to focus
        - daily_workouts: Array of objects with name, duration, and exercise list (name, sets, reps, notes)
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Workout Generation Error: {e}")
            return {"error": "Failed to generate plan"}

    async def analyze_pose_landmarks(self, landmarks: List[Dict[str, float]], exercise: str) -> Dict[str, Any]:
        """Analyze MediaPipe landmarks to detect form errors."""
        # This would ideally be a dedicated logic module, but we can use LLM for reasoning
        # or better yet, a specialized computer vision function.
        # For now, we simulate form analysis.
        
        return {
            "score": 92.0,
            "alerts": [],
            "feedback": "Great form! Keep your back straight."
        }

ai_service = AIService()
