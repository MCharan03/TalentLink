from app import db
from app.models import UserData, CareerForecast
from app.utils.ai_utils import _call_gemini
import json
from datetime import datetime

class CareerForecastService:
    def __init__(self, user_id):
        self.user_id = user_id
        
    def generate_forecast(self, target_role, time_horizon_years=2):
        """
        Generates a career forecast including a future resume and gap analysis.
        """
        # 1. Fetch current resume analysis
        user_data = UserData.query.filter_by(user_id=self.user_id).order_by(UserData.uploaded_at.desc()).first()
        
        if not user_data or not user_data.analysis_result:
            return {"error": "No resume found. Please upload a resume first."}
        
        current_profile = user_data.analysis_result
        current_skills = current_profile.get('actual_skills', [])
        
        # 2. Construct Prompt for Gemini
        prompt = f"""
        You are an advanced Career Architect AI. 
        Your task is to build a realistic 'Future Career Simulation' for a user who wants to become a '{target_role}' in {time_horizon_years} years.

        Current Profile:
        - Detected Skills: {current_skills}
        - Experience Level: {current_profile.get('experience_level', 'Unknown')}
        - Current Field: {current_profile.get('predicted_field', 'Unknown')}

        Target Goal:
        - Role: {target_role}
        - Timeframe: {time_horizon_years} years

        Task:
        1. **Gap Analysis**: Identify the specific hard and soft skills missing between the current profile and the target role.
        2. **Future Resume Simulation**: Generate the JSON for what this user's resume *should* look like in {time_horizon_years} years IF they follow an optimal path. Invent 1-2 realistic "future job experiences" or "promotions" they would need to achieve.
        3. **Roadmap**: Create a quarterly timeline of milestones.

        Return a JSON object with this exact structure:
        {{
            "target_role": "{target_role}",
            "gap_analysis": {{
                "missing_hard_skills": ["Skill 1", "Skill 2"],
                "missing_soft_skills": ["Skill A", "Skill B"],
                "critical_projects_needed": ["Project Idea 1", "Project Idea 2"]
            }},
            "future_resume": {{
                "summary": "A hypothetical professional summary for the future role...",
                "added_experience": [
                    {{
                        "title": "Intermediate Role Title",
                        "company": "Top Tier Tech Company (Hypothetical)",
                        "duration": "18 months",
                        "key_achievements": ["Achievement 1", "Achievement 2"]
                    }}
                ],
                "projected_skills": ["List of all skills (current + new)"]
            }},
            "roadmap_timeline": [
                {{
                    "quarter": "Q1 2026",
                    "milestone": "Master Kubernetes",
                    "action_items": ["Take Course X", "Build Project Y"]
                }},
                {{
                     "quarter": "Q3 2026",
                     "milestone": "Lead a small team",
                     "action_items": ["Mentor a junior", "Manage a sprint"]
                }}
                // Generate 4-6 milestones
            ],
            "success_probability": 85, 
            "motivational_message": "A short, encouraging message..."
        }}
        """

        # 3. Call Gemini
        result = _call_gemini(prompt, response_mime_type='application/json')
        
        if not result:
            return {"error": "AI Service failed to generate forecast."}
            
        # 4. Save to Database
        forecast = CareerForecast(
            user_id=self.user_id,
            target_role=target_role,
            future_resume_json=result.get('future_resume'),
            gap_analysis=result.get('gap_analysis'),
            roadmap_timeline=result.get('roadmap_timeline'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(forecast)
        db.session.commit()
        
        return result

    def get_latest_forecast(self):
        return CareerForecast.query.filter_by(user_id=self.user_id).order_by(CareerForecast.created_at.desc()).first()
