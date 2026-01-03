from app import create_app
from app.utils.vector_utils import index_all_jobs

app = create_app()

if __name__ == "__main__":
    print("Indexing all jobs to Vector DB...")
    index_all_jobs(app)
    print("Indexing complete.")
