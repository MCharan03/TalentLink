import google.generativeai as genai
from flask import current_app
import json

class InterviewCoach:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in config")
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
        return self._model

    def analyze_response(self, question, answer):
        """
        Analyzes a candidate's answer to a specific question.
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
        
        try:
            response = self.model.generate_content(prompt)
            # Clean potential markdown code blocks
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            return {
                "score": 0,
                "sentiment": "error",
                "feedback": "Could not analyze response.",
                "improvement_tip": str(e),
                "keywords_detected": []
            }

interview_coach = InterviewCoach()
