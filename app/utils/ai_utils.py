from google import genai
from google.genai import types
import os
import json
import time
import random
from functools import wraps

# Initialize the client with the API key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        print(f"Failed after {retries} retries: {e}")
                        raise
                    sleep = (backoff_in_seconds * 2 **
                             x + random.uniform(0, 1))
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator


@retry_with_backoff()
def _call_gemini(prompt, response_mime_type=None):
    """
    Helper function to call Gemini API with error handling and optional JSON parsing.
    """
    try:
        config = types.GenerateContentConfig(
            response_mime_type=response_mime_type) if response_mime_type else None

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=config
        )

        if response_mime_type == 'application/json':
            return json.loads(response.text)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None


def analyze_resume(resume_text, job_description):
    """
    Analyzes a resume against a job description using the Gemini API.
    """
    prompt = f"""Analyze the following resume and return a JSON object with the following structure:
    {{
        "name": "<The candidate's name>",
        "email": "<The candidate's email address>",
        "contact_number": "<The candidate's contact number>",
        "experience_level": "<The candidate's experience level (e.g., Fresher, Intermediate, Experienced)>",
        "predicted_field": "<The predicted job field for the candidate>",
        "resume_score": <An integer score for the resume out of 100, based on formatting, skills, and achievements>,
        "actual_skills": ["<A list of skills extracted from the resume>"],
        "recommended_skills": ["<A list of recommended skills for the predicted field>"],
        "recommended_courses": ["<A list of recommended courses for the predicted field>"],
        "ai_summary": "<A detailed analysis of the resume's strengths and weaknesses, with specific, actionable suggestions for improvement in the summary, projects, and achievements sections. Also include advice on how to make the resume more ATS-friendly. Critically evaluate the action verbs used and suggest stronger alternatives where appropriate. Provide feedback on overall formatting, readability, and consistency, inferring these from the text structure. The feedback should be comprehensive and descriptive.>",
        "quantifiable_achievements_suggestions": ["<A list of suggestions for adding more quantifiable achievements to the resume. For example, 'Instead of saying you were responsible for sales, try to quantify your impact, like 'Increased sales by 15% over 6 months'.'>"],
        "formatting_analysis": "<A detailed analysis of the resume's formatting, including feedback on font consistency, spacing, layout, and use of white space. Provide specific suggestions for improvement.>"
    }}

    Resume:\n{resume_text}"""

    if job_description:
        prompt += f"""

    Additionally, consider the following job description for a more tailored analysis:
    Job Description:\n{job_description}

    In the 'ai_summary', also provide a semantic match score (out of 100) between the resume and the job description, and suggest specific areas where the resume could be improved to better align with the job description's requirements, even if exact keywords are not present. Focus on conceptual alignment and thematic relevance.
    """

    result = _call_gemini(prompt, response_mime_type='application/json')

    if not result:
        return {
            "resume_score": 0,
            "actual_skills": [],
            "matching_skills": [],
            "missing_skills": [],
            "ai_summary": "Error during analysis. Please try again.",
            "improvement_suggestions": "Could not analyze the resume.",
            "predicted_field": "N/A",
            "experience_level": "N/A",
            "recommended_skills": [],
            "recommended_courses": [],
            "quantifiable_achievements_suggestions": [],
            "formatting_analysis": "N/A",
            "name": "N/A",
            "email": "N/A",
            "contact_number": "N/A"
        }
    return result


def generate_job_description(job_title):
    """
    Generates a job description using the Gemini API.
    """
    prompt = f"""
    Generate a detailed and professional job description for the following job title: {job_title}.
    Include sections for Responsibilities, Qualifications, and Benefits.
    """
    return _call_gemini(prompt) or "Error generating job description."


def get_interview_question(answer, stage="continue"):
    """
    Gets the next interview question from the Gemini API.
    """
    if stage == "start":
        prompt = "You are an interviewer. Your first question is: 'Tell me about yourself.'"
    else:
        prompt = f"""
        You are an interviewer. The candidate's previous answer was:
        '{answer}'
        
        Ask a relevant follow-up question.
        """
    return _call_gemini(prompt) or "I'm sorry, I had an issue generating the next question. Let's try again."


def generate_mock_test(topic, num_questions=5):
    """
    Generates a mock test using the Gemini API.
    """
    prompt = f"""
    Generate a multiple-choice test on the topic of '{topic}'.
    Provide {num_questions} questions in JSON format with the following structure:
    {{
        "questions": [
            {{
                "question": "...",
                "options": ["...", "...", "...", "..."],
                "correct_answer": "..."
            }}
        ]
    }}
    Return only the JSON object.
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def generate_linkedin_content(role, skills, achievements):
    """
    Generates LinkedIn profile content using the Gemini API.
    """
    prompt = f"""
    Generate professional LinkedIn profile content for a '{role}'.
    
    Key Skills: {skills}
    Key Achievements: {achievements}
    
    Provide the content in JSON format with the following keys:
    - "headline": A catchy and professional headline.
    - "about": A compelling 'About' section summary (approx 2 paragraphs).
    - "experience_bullets": A list of 3-5 strong bullet points describing the achievements for the Experience section.
    
    Return only the JSON object.
    """
    result = _call_gemini(prompt, response_mime_type='application/json')
    if not result:
        return {
            "headline": "Error generating content",
            "about": "Please try again later.",
            "experience_bullets": []
        }
    return result


def generate_next_assessment_question(conversation_history, predicted_field, experience_level):
    """
    Generates the next assessment question based on history.
    """
    if len(conversation_history) >= 3:
        return {"status": "completed"}

    prompt = f"""You are an expert career coach conducting an assessment.
    The candidate's predicted field is '{predicted_field}' and their experience level is '{experience_level}'.
    Here is the conversation history: {conversation_history}

    Based on this, generate the next single multiple-choice question to probe their skills.
    If the history is empty, ask a broad opening question related to the field.
    After 3 questions, return a status of 'completed'.
    
    Return a JSON object with 'status', 'question', 'options', and 'answer'.
    Example: {{"status": "in_progress", "question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}
    """

    result = _call_gemini(prompt, response_mime_type='application/json')
    if not result:
        return {"status": "completed"}
    return result


def generate_updated_analysis(initial_analysis, conversation_history):
    """
    Generates an updated analysis based on assessment answers.
    """
    prompt = f"""Given the initial resume analysis and the candidate's answers in the assessment, provide an updated analysis.
    Initial Analysis: {initial_analysis}
    Assessment History: {conversation_history}

    The updated analysis should:
    1. Refine 'ai_summary' with insights from the assessment.
    2. Provide more specific 'recommended_skills' and 'recommended_courses'.
    3. Add a new 'how_to_improve' section with actionable advice.

    Return a JSON object with the updated fields.
    """
    result = _call_gemini(prompt, response_mime_type='application/json')
    if result:
        initial_analysis.update(result)
    return initial_analysis
