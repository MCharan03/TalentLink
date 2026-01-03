import requests
import base64
from .ai_utils import _call_gemini

GITHUB_API_URL = "https://api.github.com"

def get_pinned_repos(username):
    # GitHub API doesn't have a direct "pinned" endpoint for public use easily without scraping or GraphQL.
    # For MVP, we'll fetch the most recent non-fork repositories.
    url = f"{GITHUB_API_URL}/users/{username}/repos?sort=updated&per_page=5"
    try:
        response = requests.get(url)
        response.raise_for_status()
        repos = response.json()
        # Filter out forks to focus on original work
        return [r for r in repos if not r.get('fork')]
    except Exception as e:
        print(f"GitHub API Error: {e}")
        return []

def get_repo_content(username, repo_name):
    # Fetch README content
    readme_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/readme"
    try:
        response = requests.get(readme_url)
        if response.status_code == 200:
            data = response.json()
            # GitHub API returns content in base64
            content = base64.b64decode(data['content']).decode('utf-8')
            return content
    except Exception as e:
        print(f"Error fetching README for {repo_name}: {e}")
        pass
    return ""

def analyze_github_profile(username):
    """
    Fetches user's recent repositories and sends a summary to Gemini for analysis.
    """
    repos = get_pinned_repos(username)
    if not repos:
        return {"error": "No repositories found or user does not exist."}
    
    repo_summaries = []
    for repo in repos:
        name = repo['name']
        description = repo['description'] or "No description"
        language = repo['language'] or "Unknown"
        stars = repo['stargazers_count']
        readme = get_repo_content(username, name)
        
        # Limit readme length to avoid token limits
        repo_summary = (
            f"Repo Name: {name}\n"
            f"Main Language: {language}\n"
            f"Stars: {stars}\n"
            f"Description: {description}\n"
            f"README Excerpt: {readme[:1000]}\n"
            "---"
        )
        repo_summaries.append(repo_summary)
    
    combined_context = "\n\n".join(repo_summaries)
    
    prompt = f"""
    You are a Senior Tech Recruiter and Code Quality Auditor.
    Analyze the following GitHub portfolio data for user '{username}'. These are their most recent original projects.
    
    Repositories Data:
    {combined_context}
    
    Task:
    1.  **Coder Persona:** Describe their coding style and focus area (e.g., "Backend specialist focused on automation tools" or "Frontend developer with a keen eye for UI").
    2.  **Hard Skills Verification:** Identify skills that are *proven* by this code, not just listed.
    3.  **Quality Assessment:** Estimate code documentation habits and project maturity based on READMEs and descriptions.
    
    Return a JSON object with this structure:
    {{
        "coder_persona": "String summary",
        "verified_skills": ["Skill 1", "Skill 2", ...],
        "code_quality_score": <Integer 1-100>,
        "quality_explanation": "String explaining the score",
        "project_highlights": [
            {{"name": "Repo Name", "insight": "Why this project stands out"}}
        ],
        "improvement_tips": ["Tip 1", "Tip 2"]
    }}
    """
    
    result = _call_gemini(prompt, response_mime_type='application/json')
    if not result:
        return {"error": "AI analysis failed."}
    
    return result
