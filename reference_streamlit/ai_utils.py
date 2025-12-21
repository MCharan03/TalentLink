import streamlit as st
import re
import json
import google.generativeai as genai
from logger_config import logger
import time
import random


def retry_with_backoff(func):
    def wrapper(*args, **kwargs):
        max_retries = 5
        base_delay = 1  # seconds
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "429 Quota Exceeded" in str(e) or "Quota exceeded" in str(e):
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** i) + \
                        (random.uniform(0, 1) * 0.1)
                    logger.warning(
                        f"Quota exceeded. Retrying {func.__name__} in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    raise  # Re-raise other exceptions immediately
        raise Exception(
            f"Failed after {max_retries} retries due to quota issues.")
    return wrapper


@st.cache_resource
def get_gemini_model():
    genai.configure(api_key=st.secrets["google_ai"]["api_key"])
    return genai.GenerativeModel('gemini-2.5-flash-lite')


def extract_json_from_response(response_text):
    """Extracts a JSON object from a string, handling markdown code blocks."""
    # First, try to find the JSON within markdown code blocks
    match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback to the broader search if markdown parsing fails
            pass

    # If no markdown block, find the first '{' and last '}'
    try:
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')
        if start_index != -1 and end_index != -1:
            json_str = response_text[start_index:end_index+1]
            return json.loads(json_str)
        else:
            return None
    except json.JSONDecodeError:
        return None


@retry_with_backoff
def generate_resume_analysis(resume_text, job_description=None):
    logger.info("Generating resume analysis.")
    try:
        model = get_gemini_model()

        base_prompt = f"""Analyze the following resume and return a JSON object with the following structure:
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
            job_description_prompt = f"""

        Additionally, consider the following job description for a more tailored analysis:
        Job Description:\n{job_description}

        In the 'ai_summary', also provide a semantic match score (out of 100) between the resume and the job description, and suggest specific areas where the resume could be improved to better align with the job description's requirements, even if exact keywords are not present. Focus on conceptual alignment and thematic relevance.
        """
            prompt = base_prompt + job_description_prompt
        else:
            prompt = base_prompt

        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info("Successfully generated resume analysis.")
            return json_data
        else:
            logger.error(
                "Could not find or parse JSON object in the AI response for resume analysis.")
            st.error("Could not find JSON object in the response.")
            st.text_area("Full response:", response.text)
            return None
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        st.error(f"Error generating AI analysis: {e}")
        return None


@retry_with_backoff
def generate_mock_test(predicted_field, experience_level, num_questions=5):
    logger.info(
        f"Generating mock test for field: {predicted_field}, level: {experience_level}")
    try:
        model = get_gemini_model()
        prompt = f"""Create a mock technical test with {num_questions} questions for a candidate with the following profile:
        - Predicted Field: {predicted_field}
        - Experience Level: {experience_level}

        The test should be adaptive, meaning the difficulty of the questions should vary. For each question, provide:
        - The question itself.
        - Four multiple-choice options (A, B, C, D).
        - The correct answer (A, B, C, or D).
        - A brief explanation of the correct answer.

        Return the test as a JSON object with a single key "questions" which is a list of question objects.
        """
        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info("Successfully generated mock test.")
            return json_data
        else:
            logger.error(
                "Could not find or parse JSON object in the AI response for mock test generation.")
            st.error("Could not find JSON object in the response.")
            st.text_area("Full response:", response.text)
            return None
    except Exception as e:
        logger.error(f"Error generating mock test: {e}")
        st.error(f"Error generating mock test: {e}")
        return None


@retry_with_backoff
def generate_mock_interview(predicted_field, experience_level, num_questions=3):
    logger.info(
        f"Generating mock interview for field: {predicted_field}, level: {experience_level}")
    try:
        model = get_gemini_model()
        prompt = f"""Create a mock interview with {num_questions} questions for a candidate with the following profile:
        - Predicted Field: {predicted_field}
        - Experience Level: {experience_level}

        The interview should include a mix of behavioral and technical questions. For each question, provide:
        - The question itself.
        - The type of question (Behavioral or Technical).

        Return the interview as a JSON object with a single key "questions" which is a list of question objects.
        """
        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info("Successfully generated mock interview questions.")
            return json_data
        else:
            logger.error(
                "Could not find or parse JSON object in the AI response for mock interview generation.")
            st.error("Could not find JSON object in the response.")
            st.text_area("Full response:", response.text)
            return None
    except Exception as e:
        logger.error(f"Error generating mock interview: {e}")
        st.error(f"Error generating mock interview: {e}")
        return None


@retry_with_backoff
def get_interview_feedback(interview_history):
    logger.info("Getting interview feedback.")
    try:
        model = get_gemini_model()
        prompt = f"""Analyze the following interview answers. For each question, assess the user's answer. Provide an overall summary of the candidate's performance.
        Based on the entire interview, provide a final recommendation.

        Interview History:
        {interview_history}

        Return a JSON object with three keys:
        1. "overall_summary": A string summarizing the performance.
        2. "recommendation": A string, which must be one of the following options: "Strong Hire", "Hire", "Leaning No", "No Hire".
        3. "justification": A string explaining the reason for your recommendation.
        """
        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info("Successfully generated interview feedback.")
            return json_data
        else:
            logger.error(
                "Could not find or parse JSON object in the AI response for interview feedback.")
            st.error("Could not find JSON object in the response.")
            st.text_area("Full response:", response.text)
            return None
    except Exception as e:
        logger.error(f"Error generating interview feedback: {e}")
        st.error(f"Error generating interview feedback: {e}")
        return None


@retry_with_backoff
def generate_next_question(conversation_history, predicted_field, experience_level):
    logger.info("Generating next assessment question.")
    try:
        model = get_gemini_model()

        prompt = f"""You are an expert career coach conducting an assessment.
        The candidate's predicted field is '{predicted_field}' and their experience level is '{experience_level}'.
        Here is the conversation history: {conversation_history}

        Based on this, generate the next single multiple-choice question to probe their skills.
        If the history is empty, ask a broad opening question related to the field.
        After 3 questions, return a status of 'completed'.
        
        Return a JSON object with 'status', 'question', 'options', and 'answer'.
        Example: {{"status": "in_progress", "question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}
        """

        if len(conversation_history) >= 3:
            return {"status": "completed"}

        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            return json_data
        else:
            logger.warning(
                "Could not parse JSON for next assessment question, ending assessment.")
            return {"status": "completed"}

    except Exception as e:
        logger.error(f"Error generating next question: {e}")
        st.error(f"Error generating next question: {e}")
        return {"status": "completed"}


@retry_with_backoff
def generate_updated_analysis(initial_analysis, conversation_history):
    logger.info("Generating updated analysis.")
    try:
        model = get_gemini_model()

        prompt = f"""Given the initial resume analysis and the candidate's answers in the assessment, provide an updated analysis.
        Initial Analysis: {initial_analysis}
        Assessment History: {conversation_history}

        The updated analysis should:
        1. Refine 'ai_summary' with insights from the assessment.
        2. Provide more specific 'recommended_skills' and 'recommended_courses'.
        3. Add a new 'how_to_improve' section with actionable advice.

        Return a JSON object with the updated fields.
        """
        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info("Successfully generated updated analysis.")
            initial_analysis.update(json_data)
            return initial_analysis
        else:
            logger.warning(
                "Could not parse JSON for updated analysis, returning original.")
            return initial_analysis  # Return original if parsing fails

    except Exception as e:
        logger.error(f"Error generating updated analysis: {e}")
        st.error(f"Error generating updated analysis: {e}")
        return initial_analysis


@retry_with_backoff
def generate_next_interview_question(conversation_history, predicted_field, experience_level):
    logger.info("Generating next interview question.")
    try:
        model = get_gemini_model()

        prompt_parts = ["You are an expert interviewer."]
        if predicted_field and predicted_field != 'N/A':
            prompt_parts.append(f"For a '{predicted_field}' role.")
        if experience_level and experience_level != 'N/A':
            prompt_parts.append(
                f"The candidate's experience level is '{experience_level}'.")

        prompt_parts.append(
            f"Here is the interview conversation history: {conversation_history}")
        prompt_parts.append(
            "Based on this, generate the next single interview question (can be behavioral or technical).")
        prompt_parts.append(
            "If the history is empty, ask an opening technical question. If the predicted field or experience level are generic (e.g., 'N/A'), generate more general interview questions.")
        prompt_parts.append(
            "After 3 questions, return a status of 'completed'.")
        prompt_parts.append(
            "Return a JSON object with 'status' and 'question'.")
        prompt_parts.append(
            "Example: {\"status\": \"in_progress\", \"question\": \"...\"}")

        prompt = "\n".join(prompt_parts)

        if len(conversation_history) >= 3:
            return {"status": "completed"}

        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            return json_data
        else:
            logger.warning(
                "Could not parse JSON for next interview question, ending interview.")
            return {"status": "completed"}  # Fallback

    except Exception as e:
        logger.error(f"Error generating next interview question: {e}")
        st.error(f"Error generating next interview question: {e}")
        return {"status": "completed"}


def generate_job_description(job_title):
    logger.info(f"Generating job description for title: {job_title}")
    try:
        model = get_gemini_model()
        prompt = f"""You are an expert HR manager. Given the job title '{job_title}', generate a comprehensive job description and a comma-separated list of recommended skills for this role.

        Return a JSON object with two keys: 'description' and 'skills'.
        The 'description' should be a detailed paragraph.
        The 'skills' should be a single string of comma-separated values.
        """
        response = model.generate_content(prompt)
        json_data = extract_json_from_response(response.text)
        if json_data:
            logger.info(
                f"Successfully generated job description for title: {job_title}")
            return json_data
        else:
            logger.error(
                f"Could not generate job description for title: {job_title}")
            st.error("Could not generate job description.")
            return None
    except Exception as e:
        logger.error(
            f"Error generating job description for title {job_title}: {e}")
        st.error(f"Error generating job description: {e}")
        return None
