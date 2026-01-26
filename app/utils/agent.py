from ..models import UserData, JobPosting
from .ai_utils import _call_gemini
import json

class CareerAgent:
    def __init__(self, user):
        self.user = user

    def _get_user_context(self):
        """
        Retrieves relevant context about the user from the database.
        """
        latest_resume = UserData.query.filter_by(user_id=self.user.id).order_by(UserData.uploaded_at.desc()).first()
        
        context = {
            "name": self.user.username,
            "resume_summary": "No resume uploaded yet.",
            "top_skills": [],
            "predicted_field": "General",
            "experience_level": "Unknown"
        }

        if latest_resume and latest_resume.analysis_result:
            result = latest_resume.analysis_result
            context["resume_summary"] = result.get('ai_summary', 'No summary available.')
            context["top_skills"] = result.get('actual_skills', [])[:10]
            context["predicted_field"] = result.get('predicted_field', 'General')
            context["experience_level"] = result.get('experience_level', 'Unknown')
            
        return context

    def chat(self, user_message, history=None):
        """
        Generates a response using Gemini, aware of the user's resume context.
        """
        context = self._get_user_context()
        
        # Build History String
        history_str = ""
        if history:
            # Limit history to last 3 turns to save tokens
            recent_history = history[-6:] 
            for msg in recent_history:
                role = "User" if msg.get('role') == 'user' else "Cherry"
                history_str += f"{role}: {msg.get('content')}\n"

        # System Prompt construction
        system_prompt = f"""
        You are 'Cherry', a highly intelligent and empathetic Career Agent. 
        You are integrated into a smart resume analysis platform.
        
        Your Goal: Help the user {context['name']} achieve their career goals.
        
        User Context:
        - Field: {context['predicted_field']}
        - Experience Level: {context['experience_level']}
        - Key Skills: {', '.join(context['top_skills'])}
        - Resume Summary: {context['resume_summary'][:500]}...
        
        Conversation History:
        {history_str}
        
        Guidelines:
        1. Be professional yet warm and encouraging.
        2. Use the provided context to give specific advice (e.g., if they ask about jobs, mention their specific skills).
        3. If they ask about their resume, refer to the 'Resume Summary' context.
        4. Keep responses concise (max 3-4 sentences unless a deep explanation is requested).
        5. If asked to find jobs, you can simulate a search or tell them to check the 'Jobs' tab.
        
        User: {user_message}
        Cherry:"""
        
        response = _call_gemini(system_prompt)
        
        if not response:
            return "I'm having a little trouble connecting to my brain right now. Please try again!"
            
        return response
