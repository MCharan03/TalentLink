from flask import current_app, url_for
import json
from app.models import UserData, MockInterview, db
from app.utils.ai_utils import get_interview_question, generate_interview_report, _call_ai

class InterviewService:
    def __init__(self):
        pass

    def get_user_context(self, user_id):
        """Fetches relevant context (skills, field) for the user."""
        user_data = UserData.query.filter_by(user_id=user_id).order_by(UserData.uploaded_at.desc()).first()
        if user_data and user_data.analysis_result:
            return {
                'field': user_data.analysis_result.get('predicted_field', 'General'),
                'level': user_data.analysis_result.get('experience_level', 'N/A'),
                'skills': user_data.analysis_result.get('actual_skills', []),
                'summary': user_data.analysis_result.get('ai_summary', '')[:500]
            }
        return None

    def get_next_question(self, last_answer, stage="continue", context=None):
        """Generates the next interview question."""
        # Using the existing utility for consistency, but wrapping it here allows for future expansion
        # (e.g., caching, logging, switching AI providers)
        return get_interview_question(last_answer, stage, resume_context=context)

    def analyze_response(self, question, answer):
        """
        Analyzes a candidate's answer to a specific question (Real-time feedback).
        """
        prompt = f"""
        You are an expert technical interview coach. 
        Question: "{question}"
        Candidate Answer: "{answer}"
        
        Provide a JSON response with:
        1. "score": integer 1-10
        2. "sentiment": "positive", "neutral", or "negative"
        3. "feedback": A concise 1-sentence feedback.
        4. "improvement_tip": A specific technical or soft-skill improvement.
        5. "keywords_detected": list of relevant technical keywords used.
        
        Return ONLY valid JSON.
        """
        result = _call_ai(prompt, response_mime_type='application/json')
        if not result:
            return {
                "score": 0,
                "sentiment": "error",
                "feedback": "Could not analyze response.",
                "improvement_tip": "AI Service unavailable",
                "keywords_detected": []
            }
        return result

    def finalize_interview(self, user, transcript_list):
        """
        Generates the final report and saves the interview session to the database.
        Returns the ID of the saved interview or None on failure.
        """
        if not transcript_list:
            return None, "No transcript provided."

        full_transcript = "\n".join(transcript_list)
        
        # Generate AI Report
        report = generate_interview_report(full_transcript)
        
        if report:
            try:
                interview_record = MockInterview(
                    user_id=user.id,
                    transcript=full_transcript,
                    feedback=json.dumps(report),
                    score=report.get('overall_score', 0)
                )
                db.session.add(interview_record)
                db.session.commit()
                return interview_record.id, None
            except Exception as e:
                db.session.rollback()
                return None, str(e)
        
        return None, "Failed to generate report."

# Singleton instance
interview_service = InterviewService()