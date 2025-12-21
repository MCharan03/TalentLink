from ai_utils import extract_json_from_response, generate_resume_analysis
import sys
import os
import pytest
import json
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to allow imports from the main project
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


# Test cases for extract_json_from_response

def test_extract_json_from_response_valid_markdown():
    text = """json
{"key": "value"}
"""
    expected = {"key": "value"}
    assert extract_json_from_response(text) == expected


def test_extract_json_from_response_valid_plain_json():
    text = 'Some text before {"key": "value"} some text after'
    expected = {"key": "value"}
    assert extract_json_from_response(text) == expected


def test_extract_json_from_response_no_json():
    text = "This is just plain text."
    assert extract_json_from_response(text) is None


def test_extract_json_from_response_invalid_json():
    text = """json
{"key": "value",
"""
    assert extract_json_from_response(text) is None

# Test cases for generate_resume_analysis using mocking


@patch('ai_utils.get_gemini_model')
def test_generate_resume_analysis_success(mock_get_gemini_model):
    mock_model = MagicMock()
    mock_get_gemini_model.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = '''json
{"name": "Test User", "email": "test@example.com", "ai_summary": "Good resume."}
'''
    mock_model.generate_content.return_value = mock_response

    resume_text = "Some resume content"
    result = generate_resume_analysis(resume_text)

    assert result is not None
    assert result["name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["ai_summary"] == "Good resume."
    mock_model.generate_content.assert_called_once()


@patch('ai_utils.get_gemini_model')
def test_generate_resume_analysis_with_job_description_success(mock_get_gemini_model):
    mock_model = MagicMock()
    mock_get_gemini_model.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = '''json
{"name": "Test User", "email": "test@example.com", "ai_summary": "Good resume with job match."}
'''
    mock_model.generate_content.return_value = mock_response

    resume_text = "Some resume content"
    job_description = "Some job description"
    result = generate_resume_analysis(resume_text, job_description)

    assert result is not None
    assert result["name"] == "Test User"
    assert result["ai_summary"] == "Good resume with job match."
    mock_model.generate_content.assert_called_once()
    # Verify that the prompt includes the job description
    args, kwargs = mock_model.generate_content.call_args
    assert "Additionally, consider the following job description" in args[0]
    assert job_description in args[0]


@patch('ai_utils.get_gemini_model')
def test_generate_resume_analysis_ai_returns_invalid_json(mock_get_gemini_model):
    mock_model = MagicMock()
    mock_get_gemini_model.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = "This is not JSON."
    mock_model.generate_content.return_value = mock_response

    resume_text = "Some resume content"
    result = generate_resume_analysis(resume_text)

    assert result is None
    mock_model.generate_content.assert_called_once()


@patch('ai_utils.get_gemini_model')
def test_generate_resume_analysis_exception_handling(mock_get_gemini_model):
    mock_model = MagicMock()
    mock_get_gemini_model.return_value = mock_model
    mock_model.generate_content.side_effect = Exception("API Error")

    resume_text = "Some resume content"
    result = generate_resume_analysis(resume_text)

    assert result is None
    mock_model.generate_content.assert_called_once()


@patch('ai_utils.get_gemini_model')
def test_generate_resume_analysis_with_new_fields_success(mock_get_gemini_model):
    mock_model = MagicMock()
    mock_get_gemini_model.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = '''json
{"name": "Test User", "email": "test@example.com", "ai_summary": "Good resume.", "quantifiable_achievements_suggestions": ["Quantify sales increase."], "formatting_analysis": "Good formatting.", "resume_score": 80, "experience_level": "Experienced", "predicted_field": "Software Engineer", "actual_skills": ["Python"], "recommended_skills": ["Go"], "recommended_courses": ["Go Course"], "contact_number": "123-456-7890"}
'''
    mock_model.generate_content.return_value = mock_response

    resume_text = "Some resume content"
    result = generate_resume_analysis(resume_text)

    assert result is not None
    assert result["name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["ai_summary"] == "Good resume."
    assert "quantifiable_achievements_suggestions" in result
    assert result["quantifiable_achievements_suggestions"] == [
        "Quantify sales increase."]
    assert "formatting_analysis" in result
    assert result["formatting_analysis"] == "Good formatting."
    mock_model.generate_content.assert_called_once()
