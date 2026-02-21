import pytest
from unittest.mock import patch, MagicMock
from app.services.interview_service import interview_service
from app.models import User, UserData, MockInterview, db
import json

def test_get_user_context(app):
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        
        # Add mock user data
        analysis = {
            "predicted_field": "Software Engineering",
            "experience_level": "Mid",
            "actual_skills": ["Java", "Spring"],
            "ai_summary": "Expert dev"
        }
        user_data = UserData(user_id=user.id, resume_path="test.pdf", analysis_result=analysis)
        db.session.add(user_data)
        db.session.commit()
        
        context = interview_service.get_user_context(user.id)
        assert context['field'] == "Software Engineering"
        assert context['level'] == "Mid"
        assert "Java" in context['skills']

def test_finalize_interview(app):
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        transcript = ["AI: Question 1", "User: Answer 1"]
        
        mock_report = {
            "overall_score": 85,
            "feedback": "Great job",
            "strengths": ["Clear communication"]
        }
        
        with patch('app.services.interview_service.generate_interview_report') as mock_gen:
            mock_gen.return_value = mock_report
            
            interview_id, error = interview_service.finalize_interview(user, transcript)
            
            assert interview_id is not None
            assert error is None
            
            # Verify it's in DB
            record = MockInterview.query.get(interview_id)
            assert record.user_id == user.id
            assert record.score == 85
            assert "AI: Question 1" in record.transcript

def test_analyze_response_mocked(app):
    with app.app_context():
        # Mocking the model attribute which triggers genai config
        with patch.object(interview_service, '_model', create=True) as mock_model:
            mock_response = MagicMock()
            mock_response.text = '{"score": 9, "sentiment": "positive", "feedback": "Nice!", "improvement_tip": "None", "keywords_detected": ["Python"]}'
            mock_model.generate_content.return_value = mock_response
            
            result = interview_service.analyze_response("Q", "A")
            
            assert result['score'] == 9
            assert result['sentiment'] == "positive"
            assert "Python" in result['keywords_detected']
