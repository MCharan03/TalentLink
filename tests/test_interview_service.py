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

def test_get_next_question_with_params(app):
    """Test that get_next_question accepts and passes new parameters."""
    with app.app_context():
        with patch('app.services.interview_service.get_interview_question') as mock_q:
            mock_q.return_value = "Tell me about a challenging project."
            
            result = interview_service.get_next_question(
                "I have 5 years of experience", "continue",
                context={"field": "Software Engineering"},
                interview_type="behavioral",
                difficulty="hard",
                round_number=3,
                conversation_history=["AI: Tell me about yourself.", "User: I'm a dev."]
            )
            
            assert result == "Tell me about a challenging project."
            mock_q.assert_called_once_with(
                "I have 5 years of experience", "continue",
                resume_context={"field": "Software Engineering"},
                interview_type="behavioral",
                difficulty="hard",
                round_number=3,
                conversation_history=["AI: Tell me about yourself.", "User: I'm a dev."]
            )

def test_finalize_interview_stores_type_and_difficulty(app):
    """Test that finalize_interview saves interview_type and difficulty to DB."""
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        transcript = ["AI: Question 1", "User: Answer 1"]
        
        mock_report = {
            "overall_score": 85,
            "communication_score": 80,
            "technical_score": 90,
            "behavioral_score": 75,
            "problem_solving_score": 85,
            "star_method_adherence": 70,
            "feedback": "Great job",
            "strengths": ["Clear communication"]
        }
        
        with patch('app.services.interview_service.generate_interview_report') as mock_gen:
            mock_gen.return_value = mock_report
            
            interview_id, error = interview_service.finalize_interview(
                user, transcript,
                interview_type="technical",
                difficulty="hard"
            )
            
            assert interview_id is not None
            assert error is None
            
            # Verify it's in DB with correct type/difficulty
            record = MockInterview.query.get(interview_id)
            assert record.user_id == user.id
            assert record.score == 85
            assert record.interview_type == "technical"
            assert record.difficulty == "hard"
            assert "AI: Question 1" in record.transcript

def test_analyze_response_with_star(app):
    """Test that analyze_response includes STAR fields for behavioral interviews."""
    with app.app_context():
        mock_result = {
            "score": 8,
            "sentiment": "positive",
            "feedback": "Good structured answer.",
            "improvement_tip": "Be more specific with metrics.",
            "keywords_detected": ["leadership", "team"],
            "star_adherence": 7,
            "star_feedback": "Good situation setup, action could be more specific."
        }
        
        with patch('app.services.interview_service._call_ai') as mock_ai:
            mock_ai.return_value = mock_result
            
            result = interview_service.analyze_response(
                "Tell me about a leadership challenge",
                "I led a team of 5...",
                interview_type="behavioral"
            )
            
            assert result['score'] == 8
            assert result['star_adherence'] == 7
            assert 'star_feedback' in result

def test_analyze_response_fallback(app):
    """Test fallback when AI is unavailable."""
    with app.app_context():
        with patch('app.services.interview_service._call_ai') as mock_ai:
            mock_ai.return_value = None
            
            result = interview_service.analyze_response("Q", "A")
            
            assert result['score'] == 0
            assert result['sentiment'] == "error"
            assert result['star_adherence'] == 0
