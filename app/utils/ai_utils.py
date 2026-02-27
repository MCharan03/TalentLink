try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    import ollama
except ImportError:
    ollama = None

import os
import json
import time
import random
from functools import wraps

# Initialize the client with the API key
_client = None

def get_client():
    global _client
    if genai is None:
        return None
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            return None
    return _client


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


def clean_json_string(s):
    """
    Cleans a string to extract valid JSON content, removing markdown blocks and whitespace.
    """
    if not s:
        return "{}"
    s = s.strip()
    # Remove markdown blocks if present
    if s.startswith("```"):
        # Find the first { and the last }
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1:
            s = s[start:end+1]
    return s


def _call_ollama(prompt, response_mime_type=None):
    """
    Helper function to call Ollama (local AI) with optional JSON parsing.
    """
    if ollama is None:
        print("Ollama library not installed. Please run 'pip install ollama'.")
        return None
        
    try:
        model = os.environ.get("OLLAMA_MODEL", "llama3")
        print(f"DEBUG: Calling Ollama with model '{model}'...", flush=True)
        
        if response_mime_type == 'application/json':
            response = ollama.generate(model=model, prompt=prompt, format='json')
            raw_text = response['response']
            print(f"DEBUG: Ollama response received, parsing JSON...", flush=True)
            try:
                return json.loads(clean_json_string(raw_text))
            except json.JSONDecodeError:
                print(f"ERROR: Ollama returned invalid JSON: {raw_text[:100]}...")
                return None
        else:
            response = ollama.generate(model=model, prompt=prompt)
            print("DEBUG: Ollama response received.", flush=True)
            return response['response']
    except Exception as e:
        print(f"Ollama Error: {e}", flush=True)
        return None


@retry_with_backoff()
def _call_ai(prompt, response_mime_type=None):
    """
    Generic helper function to call AI API (Gemini or Ollama).
    """
    provider = os.environ.get("AI_PROVIDER", "gemini")
    
    # Track current provider for UI/Status purposes (optional)
    os.environ["CURRENT_AI_PROVIDER"] = provider
    
    if provider == "ollama":
        return _call_ollama(prompt, response_mime_type)
        
    try:
        client = get_client()
        if not client:
            print("Gemini API Client not initialized or missing. Using Ollama fallback.")
            os.environ["CURRENT_AI_PROVIDER"] = "ollama"
            return _call_ollama(prompt, response_mime_type)

        config = types.GenerateContentConfig(
            response_mime_type=response_mime_type) if response_mime_type else None

        print(f"DEBUG: Calling Gemini API with model 'gemini-2.5-flash-lite'...", flush=True)
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=config
        )

        if response_mime_type == 'application/json':
            print("DEBUG: Gemini response received, parsing JSON...", flush=True)
            try:
                return json.loads(clean_json_string(response.text))
            except json.JSONDecodeError:
                 print(f"ERROR: Gemini returned invalid JSON. Attempting Ollama fallback.")
                 os.environ["CURRENT_AI_PROVIDER"] = "ollama"
                 return _call_ollama(prompt, response_mime_type)
        
        print("DEBUG: Gemini response received.", flush=True)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}. Attempting Ollama fallback.", flush=True)
        os.environ["CURRENT_AI_PROVIDER"] = "ollama"
        return _call_ollama(prompt, response_mime_type)


def _call_gemini(prompt, response_mime_type=None):
    """
    Legacy alias for _call_ai.
    """
    return _call_ai(prompt, response_mime_type)


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
        "learning_roadmap": [
            {{
                "week": "Week 1",
                "topic": "<Focus topic>",
                "description": "<What to learn>",
                "search_query": "<Best search query for this topic>"
            }},
             {{
                "week": "Week 2",
                "topic": "<Focus topic>",
                "description": "<What to learn>",
                "search_query": "<Best search query for this topic>"
            }},
             {{
                "week": "Week 3",
                "topic": "<Focus topic>",
                "description": "<What to learn>",
                "search_query": "<Best search query for this topic>"
            }},
             {{
                "week": "Week 4",
                "topic": "<Focus topic>",
                "description": "<What to learn>",
                "search_query": "<Best search query for this topic>"
            }}
        ],
        "youtube_search_queries": ["<Query 1>", "<Query 2>", "<Query 3>"],
        "ai_summary": "<A detailed analysis of the resume's strengths and weaknesses, with specific, actionable suggestions for improvement in the summary, projects, and achievements sections. Also include advice on how to make the resume more ATS-friendly. Critically evaluate the action verbs used and suggest stronger alternatives where appropriate. Provide feedback on overall formatting, readability, and consistency, inferring these from the text structure. The feedback should be comprehensive and descriptive.>",
        "quantifiable_achievements_suggestions": ["<A list of suggestions for adding more quantifiable achievements to the resume. For example, 'Instead of saying you were responsible for sales, try to quantify your impact, like 'Increased sales by 15% over 6 months'.'>"],
        "formatting_analysis": "<A detailed analysis of the resume's formatting, including feedback on font consistency, spacing, layout, and use of white space. Provide specific suggestions for improvement.>",
        "mermaid_career_path": "graph LR; A[Current Role] --> B[Next Step]; B --> C[Future Goal]"
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
            "learning_roadmap": [],
            "youtube_search_queries": [],
            "quantifiable_achievements_suggestions": [],
            "formatting_analysis": "N/A",
            "name": "N/A",
            "email": "N/A",
            "contact_number": "N/A",
            "mermaid_career_path": ""
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


def get_interview_question(answer, stage="continue", resume_context=None,
                            interview_type="mixed", difficulty="medium",
                            round_number=1, conversation_history=None):
    """
    Gets the next interview question from the Gemini API.
    Supports adaptive difficulty, interview types (behavioral/technical/mixed),
    round-based progression, and conversation history for coherent follow-ups.
    """
    if stage == "start":
        prompt = "You are an interviewer. Your first question is: 'Tell me about yourself.'"
    else:
        context_str = ""
        if resume_context:
            context_str = f"Candidate Profile Context: {resume_context}\n"
        
        # Build conversation history for context
        history_str = ""
        if conversation_history:
            recent = conversation_history[-6:]  # Last 3 Q&A pairs
            for entry in recent:
                history_str += f"{entry}\n"

        # Difficulty mapping
        difficulty_instructions = {
            "easy": "Ask straightforward, fundamental questions. Be encouraging and supportive.",
            "medium": "Ask moderately challenging questions that test practical knowledge and application.",
            "hard": "Ask advanced, scenario-based questions that require deep expertise and critical thinking."
        }
        diff_instruction = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])

        # Interview type mapping
        type_instructions = {
            "behavioral": "Focus on behavioral questions using the STAR method (Situation, Task, Action, Result). Ask about past experiences, teamwork, leadership, and conflict resolution.",
            "technical": "Focus on technical questions related to the candidate's field. Ask about algorithms, system design, debugging, and domain-specific knowledge.",
            "mixed": "Alternate between behavioral and technical questions. Use behavioral questions in odd rounds and technical questions in even rounds."
        }
        type_instruction = type_instructions.get(interview_type, type_instructions["mixed"])

        # Progressive difficulty based on round
        progression = "Opening ice-breaker phase."
        if round_number <= 2:
            progression = "Opening phase: Ask warm-up questions to put the candidate at ease."
        elif round_number <= 5:
            progression = "Core phase: Ask substantive questions that test competency and depth."
        else:
            progression = "Deep-dive phase: Ask challenging follow-up questions that probe advanced understanding."

        prompt = f"""
        You are an expert {interview_type} interviewer conducting a structured mock interview.
        
        {context_str}
        
        Interview Configuration:
        - Type: {interview_type.upper()} | {type_instruction}
        - Difficulty: {difficulty.upper()} | {diff_instruction}
        - Round: {round_number} | {progression}
        
        Conversation History:
        {history_str}
        
        The candidate's latest answer was:
        '{answer}'
        
        Task:
        1. EVALUATE: Briefly assess their answer (2-3 sentences). Was it complete? Technical accuracy? If it's a behavioral answer, evaluate STAR method adherence. If wrong, gently correct them.
        2. TRANSITION: Provide a smooth transition sentence.
        3. NEXT QUESTION: Ask the next question appropriate for the current round, difficulty, and interview type.
        
        Keep your response conversational but professional. Never repeat a question from the history.
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


def generate_professional_summary(job_title, skills):
    """
    Generates a professional resume summary using Gemini.
    """
    prompt = f"""
    Write a compelling, professional resume summary (approx 50-75 words) for a {job_title}.
    Highlight these skills: {skills}.
    The tone should be confident, modern, and suitable for a senior or mid-level candidate.
    Return a JSON object: {{ "summary": "..." }}
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def refine_experience_points(role, raw_text):
    """
    Refines raw experience text into professional bullet points.
    """
    prompt = f"""
    Rewrite the following rough experience description for a '{role}' role into 3-4 professional, quantifiable, and action-oriented resume bullet points.
    Raw Text: "{raw_text}"
    
    Use strong action verbs (e.g., "Spearheaded", "Optimized", "Engineered").
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def generate_cover_letter(resume_text, job_description):
    """
    Generates a personalized cover letter based on resume and job description.
    """
    prompt = f"""
    You are an expert career consultant. Write a highly persuasive, professional cover letter for a candidate based on their resume and the target job description.
    
    Resume Context:
    {resume_text[:4000]}
    
    Job Description:
    {job_description[:2000]}
    
    Instructions:
    - Return ONLY a JSON object with a single key: "cover_letter_text".
    - The letter should be ready to copy-paste (Subject line optional but good).
    - Highlight specific achievements from the resume that match the job requirements.
    - Tone: Professional, confident, and enthusiastic.
    - Use standard business letter formatting (Dear Hiring Manager...).
    """
    
    result = _call_gemini(prompt, response_mime_type='application/json')
    if not result:
        return {"cover_letter_text": "Error generating cover letter. Please try again."}
    return result


def optimize_linkedin_profile(profile_data):
    """
    Generates an optimized LinkedIn profile based on provided user data.
    profile_data: dict containing name, summary, jobs (list), educations (list), skills, projects (list)
    """
    prompt = f"""
    You are an expert LinkedIn profile optimizer and Career Coach. 
    Review the following raw profile data and rewrite it to be highly professional, engaging, and SEO-friendly for recruiters.

    User Input Data:
    Name: {profile_data.get('name')}
    Current Summary: {profile_data.get('summary')}
    Skills: {profile_data.get('skills')}
    
    Work Experience: {json.dumps(profile_data.get('jobs'))}
    Education: {json.dumps(profile_data.get('educations'))}
    Projects: {json.dumps(profile_data.get('projects'))}

    Generate an OPTIMIZED version of this profile in JSON format with the following keys:
    - "headline": A compelling, keyword-rich headline (max 220 chars) that highlights value proposition.
    - "about": A professional summary (first-person, engaging, 2-3 paragraphs). Focus on career story and impact.
    - "experience": A list of objects, matching the input order. Each object must have:
        - "title": Optimized Job Title.
        - "company": Company Name.
        - "location": Location.
        - "dates": Dates.
        - "description": A string containing 3-5 distinct bullet points. Use strong action verbs and quantify results where possible. 
    - "education": A list of objects with "degree", "school", "location", "dates".
    - "skills": A refined list of top 15-20 relevant skills (comma-separated string), prioritizing hard skills for the target role.
    - "projects": A list of objects with "name" and "description" (concise and impactful).

    Ensure the tone is professional, confident, yet accessible.
    """
    
    result = _call_gemini(prompt, response_mime_type='application/json')
    
    # Fallback structure if AI fails
    if not result:
        return {
            "headline": "Error optimizing profile",
            "about": "Could not generate content. Please try again.",
            "experience": [],
            "education": [],
            "skills": profile_data.get('skills', ''),
            "projects": []
        }
    return result


def tailor_resume_to_job(resume_text, job_description):
    """
    Tailors a resume to a specific job description using Gemini.
    Returns a JSON object compatible with generate_resume_pdf_from_profile.
    """
    prompt = f"""
    You are an expert Resume Writer and Career Strategist.
    Your task is to rewrite the provided resume to specifically target the given job description.
    
    Goals:
    1.  **Keywords:** Naturally incorporate keywords from the job description into the summary, skills, and experience.
    2.  **Relevance:** Prioritize experience and projects that match the job requirements.
    3.  **Impact:** Use strong action verbs and quantify results (if numbers exist in the source text, emphasize them; if not, focus on scope and outcome).
    4.  **Structure:** Return the result in the EXACT JSON format specified below.

    Source Resume:
    {resume_text}

    Target Job Description:
    {job_description}

    Required JSON Output Format:
    {{
        "name": "Candidate Name (extracted from resume)",
        "email": "Email (extracted)",
        "phone": "Phone (extracted)",
        "headline": "A targeted professional headline for this specific job",
        "about": "A professional summary tailored to this job (3-4 sentences)",
        "skills": "Comma-separated string of top skills relevant to this job",
        "experience": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "location": "Location",
                "dates": "Date Range",
                "description": "3-5 bullet points optimized for the target job."
            }}
            // ... include all relevant jobs
        ],
        "education": [
            {{
                "school": "School Name",
                "degree": "Degree",
                "dates": "Dates",
                "location": "Location (optional)"
            }}
        ],
        "projects": [
            {{
                "name": "Project Name",
                "description": "Brief description highlighting relevance to the job."
            }}
        ]
    }}
    
    IMPORTANT: Do not fabricate experience. Only rephrase and emphasize existing information to match the job.
    """
    
    return _call_gemini(prompt, response_mime_type='application/json')


def simulate_ats_parsing(resume_text):
    """
    Simulates how an ATS system parses a resume and identifies potential issues.
    """
    prompt = f"""
    You are an expert in Applicant Tracking Systems (ATS).
    Analyze the following resume text as if you were a machine parsing it.
    
    Resume Text:
    {resume_text[:5000]}
    
    Task:
    1. Identify 'Parse Failures': Sections where the text might be garbled due to columns, tables, or weird symbols.
    2. Missing Headers: Identify standard resume headers (Experience, Education, Skills) that are missing or non-standard.
    3. Keyword Density: List the top 5 most prominent keywords you found.
    4. Structural Score: Give a score (1-100) on how 'machine-readable' this resume is.
    
    Return a JSON object:
    {{
        "parsed_raw_text": "A simulated version of how a simple machine would see the text (stripped of layout)",
        "structural_score": <Int>,
        "potential_issues": ["Issue 1", "Issue 2"],
        "top_keywords": ["Keyword 1", "Keyword 2"],
        "formatting_warnings": ["Warning 1", "Warning 2"],
        "ats_friendly_score": <Int>
    }}
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def analyze_market_trends(job_descriptions_sample, user_skills_summary):
    """
    Analyzes the gap between market demand (jobs) and user supply (skills).
    """
    prompt = f"""
    You are a Chief Labor Economist for a recruitment platform.
    
    Data Provided:
    1. Sample of Recent Job Postings (Market Demand):
    {job_descriptions_sample[:10000]} ... (truncated)
    
    2. Summary of User Skills (Talent Supply):
    {user_skills_summary}
    
    Task:
    Perform a Market Gap Analysis. Identify specific skills that are in high demand but low supply among our users.
    
    Return a JSON object:
    {{
        "undersupplied_skills": ["Skill 1", "Skill 2", "Skill 3"],
        "oversupplied_skills": ["Skill A", "Skill B"],
        "emerging_trends": ["Trend 1", "Trend 2"],
        "strategic_advice": "Advice on what content/courses to add to the platform to help users...",
        "market_health_score": 75
    }}
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def generate_interview_report(transcript):
    """
    Generates a detailed performance report from an interview transcript.
    Includes per-category scoring, STAR method adherence, and per-question breakdown.
    """
    prompt = f"""
    You are an expert Interview Coach and Assessment Specialist. Analyze the following interview transcript and provide a comprehensive report card.
    
    Transcript:
    {transcript}
    
    Return a JSON object with:
    - "overall_score": (Integer 0-100)
    - "communication_score": (Integer 0-100) Score for clarity, articulation, and professional language.
    - "technical_score": (Integer 0-100) Score for technical accuracy and depth of knowledge.
    - "behavioral_score": (Integer 0-100) Score for demonstrating leadership, teamwork, and problem-solving through examples.
    - "problem_solving_score": (Integer 0-100) Score for analytical thinking and structured approach.
    - "star_method_adherence": (Integer 0-100) How well the candidate structured behavioral answers using Situation-Task-Action-Result.
    - "sentiment_analysis": "Brief summary of the candidate's tone/confidence throughout."
    - "strengths": ["Strength 1", "Strength 2", "Strength 3"]
    - "weaknesses": ["Weakness 1", "Weakness 2"]
    - "keyword_usage": "Feedback on technical keywords used or missed."
    - "improvement_tips": ["Tip 1", "Tip 2", "Tip 3"]
    - "confidence_trend": [A list of 5 integers representing confidence levels throughout the interview]
    - "question_breakdown": [
        {{"question": "Q text", "answer_score": 85, "feedback": "Brief feedback"}},
        ...for each Q&A pair in the transcript
      ]
    
    Return ONLY the JSON.
    """
    return _call_gemini(prompt, response_mime_type='application/json')


def analyze_dream_job(resume_text, target_role):
    """
    Compares current resume against a target dream role.
    """
    prompt = f"""
    You are a Strategic Career Planner. 
    Compare the following resume against the target role: "{target_role}".
    
    Resume:
    {resume_text}
    
    Task:
    Perform a Gap Analysis and return a JSON object with:
    - "match_percentage": (Integer)
    - "current_standing": "A summary of where they are now."
    - "missing_skills": ["Skill 1", "Skill 2"]
    - "required_experience": "What kind of projects/roles they need to bridge the gap."
    - "roadmap_steps": [
        {{"step": "Step 1", "description": "Short term goal", "timeframe": "1-3 months"}},
        {{"step": "Step 2", "description": "Mid term goal", "timeframe": "6-12 months"}},
        {{"step": "Step 3", "description": "Long term goal", "timeframe": "1-2 years"}}
    ]
    - "bridge_visual_data": [50, 65, 80, 100] (A list of 4 integers representing progress levels at each roadmap step)
    
    Return ONLY the JSON.
    """
    return _call_gemini(prompt, response_mime_type='application/json')
