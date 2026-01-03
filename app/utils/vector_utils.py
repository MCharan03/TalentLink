import chromadb
import os

# Initialize persistent client
# Saving to 'chroma_db' folder in the smart_resume_analyzer directory
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'chroma_db')
chroma_client = chromadb.PersistentClient(path=db_path)

# Use default embedding function (all-MiniLM-L6-v2)
job_collection = chroma_client.get_or_create_collection(name="job_postings")
resume_collection = chroma_client.get_or_create_collection(name="resumes")

def add_job_to_vector_db(job_id, title, description):
    """
    Adds a job posting to the vector database.
    """
    text = f"{title}. {description}"
    try:
        job_collection.add(
            documents=[text],
            metadatas=[{"job_id": job_id, "title": title}],
            ids=[str(job_id)]
        )
        print(f"Indexed Job {job_id} in Vector DB.")
    except Exception as e:
        print(f"Error indexing job {job_id}: {e}")

def add_resume_to_vector_db(user_id, resume_text, skills):
    """
    Adds a user's resume summary to the vector database.
    """
    # Create a rich text representation for semantic search
    text = f"Skills: {', '.join(skills)}. Resume Content: {resume_text[:1000]}"
    try:
        # Check if exists and update, or add
        existing = resume_collection.get(ids=[str(user_id)])
        if existing['ids']:
             resume_collection.update(
                documents=[text],
                metadatas=[{"user_id": user_id}],
                ids=[str(user_id)]
            )
        else:
            resume_collection.add(
                documents=[text],
                metadatas=[{"user_id": user_id}],
                ids=[str(user_id)]
            )
        print(f"Indexed User {user_id} Resume in Vector DB.")
    except Exception as e:
        print(f"Error indexing resume for user {user_id}: {e}")

def search_jobs_by_resume(resume_text, n_results=5):
    """
    Semantically searches for jobs matching the resume text.
    Returns a list of job_ids.
    """
    try:
        # Truncate resume text if too long for the model (limit is usually 512 tokens for MiniLM, 
        # Chroma handles truncation but good to be safe)
        query_text = resume_text[:2000] 
        
        results = job_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if not results['metadatas']:
            return []
            
        # Extract job_ids from metadata
        job_ids = [int(meta['job_id']) for meta in results['metadatas'][0]]
        return job_ids
    except Exception as e:
        print(f"Vector search error: {e}")
        return []

def search_resumes_by_job_description(job_description, n_results=5):
    """
    Semantically searches for resumes matching a job description.
    Returns a list of user_ids.
    """
    try:
        query_text = job_description[:2000]
        
        results = resume_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if not results['metadatas']:
            return []
            
        # Extract user_ids from metadata
        user_ids = [int(meta['user_id']) for meta in results['metadatas'][0]]
        return user_ids
    except Exception as e:
        print(f"Resume vector search error: {e}")
        return []

def index_all_jobs(app):
    """
    Utility to re-index all jobs from SQL to Chroma.
    Call this once to populate the DB.
    """
    from ..models import JobPosting
    with app.app_context():
        jobs = JobPosting.query.all()
        print(f"Found {len(jobs)} jobs to index.")
        for job in jobs:
            add_job_to_vector_db(job.id, job.title, job.description)
