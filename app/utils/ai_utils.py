import google.generativeai as genai
import os
import json

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_resume(resume_text, job_description):
    """
    Analyzes a resume against a job description using the Gemini API.
    """
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Analyze the following resume and job description.
    Provide a detailed analysis in JSON format with the following structure:
    - "score": A score from 0 to 100 representing how well the resume matches the job description.
    - "skills": A list of key skills found in the resume.
    - "matching_skills": A list of skills that are present in both the resume and the job description.
    - "missing_skills": A list of skills that are present in the job description but not in the resume.
    - "summary": A brief summary of the candidate's profile.
    - "improvement_suggestions": Actionable suggestions for the candidate to improve their resume for this specific job.

    Resume Text:
    {resume_text}

    Job Description:
    {job_description}

    Return only the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        # The response text might be enclosed in ```json ... ```, so we need to extract it.
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        print(f"Error analyzing resume with Gemini: {e}")
        return {
            "score": 0,
            "skills": [],
            "matching_skills": [],
            "missing_skills": [],
            "summary": "Error during analysis.",
            "improvement_suggestions": "Could not analyze the resume."
        }

def generate_job_description(job_title):
    """
    Generates a job description using the Gemini API.
    """
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Generate a detailed and professional job description for the following job title: {job_title}.
    Include sections for Responsibilities, Qualifications, and Benefits.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating job description with Gemini: {e}")
        return "Error generating job description."

def get_interview_question(answer, stage="continue"):
    """
    Gets the next interview question from the Gemini API.
    """
    model = genai.GenerativeModel('gemini-pro')

    if stage == "start":
        prompt = "You are an interviewer. Your first question is: 'Tell me about yourself.'"
    else:
        prompt = f"""
        You are an interviewer. The candidate's previous answer was:
        '{answer}'
        
        Ask a relevant follow-up question.
        """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting interview question from Gemini: {e}")
        return "I'm sorry, I had an issue generating the next question. Let's try again."

def generate_mock_test(topic, num_questions=5):
    """
    Generates a mock test using the Gemini API.
    """
    model = genai.GenerativeModel('gemini-pro')

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

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        print(f"Error generating mock test with Gemini: {e}")
        return None
