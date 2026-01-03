from app.models import User, UserData
from app.utils.vector_utils import search_resumes_by_job_description
from app.utils.ai_utils import _call_gemini
import json

class EmployerService:
    def search_talent(self, job_description_query):
        """
        Finds candidates matching the description.
        Returns a list of User objects with a 'match_score' (simulated for now based on rank).
        """
        user_ids = search_resumes_by_job_description(job_description_query)
        
        candidates = []
        for index, uid in enumerate(user_ids):
            user = User.query.get(uid)
            if user:
                # Rank-based score for UI
                user.match_score = 95 - (index * 5) 
                candidates.append(user)
        
        return candidates

    def get_candidate_insight(self, candidate_id, job_description):
        """
        Generates a narrative explaining why this candidate is a good fit.
        """
        user_data = UserData.query.filter_by(user_id=candidate_id).order_by(UserData.uploaded_at.desc()).first()
        
        if not user_data or not user_data.analysis_result:
            return {"error": "Candidate has no analyzed data."}
            
        profile = user_data.analysis_result
        skills = profile.get('actual_skills', [])
        summary = profile.get('ai_summary', 'No summary available.')
        
        prompt = f"""
        You are a Talent Scout AI.
        
        Candidate Profile:
        - Skills: {skills}
        - AI Summary: {summary}
        
        Target Job:
        {job_description}
        
        Task:
        Write a short "Scout's Note" (approx 3-4 sentences) to the Hiring Manager.
        Focus on the *potential* and *narrative fit*. Explain why this person might be a hidden gem or a strong contender, even if they don't have every single keyword. 
        Highlight transferrable skills.
        """
        
        insight = _call_gemini(prompt)
        return {"insight": insight}
