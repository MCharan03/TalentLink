import re
import random
from ..models import JobPosting, UserData
from .vector_utils import search_jobs_by_resume

class CareerAgent:
    def __init__(self, user):
        self.user = user

    def _detect_intent(self, message):
        """
        Simple Rule-Based Algorithm to detect user intent.
        """
        message = message.lower()
        
        # Intent: Job Search
        if any(word in message for word in ['job', 'work', 'hiring', 'position', 'vacancy', 'apply']):
            return 'search_jobs'
        
        # Intent: Resume Help
        if any(word in message for word in ['resume', 'cv', 'summary', 'skills', 'analysis', 'improve']):
            return 'resume_help'
        
        # Intent: Interview Prep
        if any(word in message for word in ['interview', 'question', 'prep', 'mock']):
            return 'interview_prep'
            
        # Intent: Greeting
        if any(word in message for word in ['hi', 'hello', 'hey', 'greetings']):
            return 'greeting'
            
        return 'unknown'

    def _search_jobs(self, query):
        """
        Executes a search using local SQL and Vector DB.
        """
        # 1. Try Vector Search first (Semantic)
        try:
            # We need text to search. If query is short, use user's last resume.
            latest_resume = UserData.query.filter_by(user_id=self.user.id).order_by(UserData.uploaded_at.desc()).first()
            search_text = query
            if latest_resume and len(query.split()) < 3:
                 search_text = str(latest_resume.analysis_result)
            
            job_ids = search_jobs_by_resume(search_text, n_results=3)
            if job_ids:
                jobs = JobPosting.query.filter(JobPosting.id.in_(job_ids)).all()
                if jobs:
                    results = "\n".join([f"- **{j.title}**: {j.description[:100]}... (ID: {j.id})" for j in jobs])
                    return f"Based on your profile, here are some top matches from our database:\n\n{results}\n\nYou can apply in the Jobs tab!"
        except:
            pass
            
        # 2. Fallback to Simple SQL Search
        jobs = JobPosting.query.limit(3).all()
        if not jobs:
            return "I currently don't have any open positions in the database. Check back later!"
            
        results = "\n".join([f"- {j.title}" for j in jobs])
        return f"Here are the latest jobs posted:\n{results}"

    def _get_resume_feedback(self):
        """
        Retrieves the latest stored AI analysis from the database.
        """
        data = UserData.query.filter_by(user_id=self.user.id).order_by(UserData.uploaded_at.desc()).first()
        if not data:
            return "I don't see a resume uploaded yet. Please go to the 'Analysis' tab to upload one!"
            
        score = data.analysis_result.get('resume_score', 0)
        summary = data.analysis_result.get('ai_summary', 'No summary available.')
        
        return f"Your latest resume score is **{score}/100**.\n\nHere is the summary:\n{summary[:300]}..."

    def chat(self, user_message, history=None):
        """
        Main Chat Algorithm.
        """
        intent = self._detect_intent(user_message)
        
        if intent == 'greeting':
            return f"Hello {self.user.username}! I am your Local Career Assistant. I can help you find jobs or review your resume."
            
        elif intent == 'search_jobs':
            return self._search_jobs(user_message)
            
        elif intent == 'resume_help':
            return self._get_resume_feedback()
            
        elif intent == 'interview_prep':
            return "To prepare for interviews, check out the 'Prep' tab! I can generate mock questions for you there."
            
        else:
            return "I'm a specialized Career Agent. Try asking me to 'find jobs' or 'check my resume'."