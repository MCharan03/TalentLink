# Project Overview: Smart Resume Screener & Analyzer

This document provides a complete overview of the Smart Resume Screener & Analyzer application, including its architecture, features, and detailed workflows.

## 1. High-Level Summary

The Smart Resume Screener & Analyzer is a web application built with Streamlit designed to be a comprehensive tool for both job seekers and recruiters. It uses Google's Generative AI to analyze resumes, provide feedback, and automate parts of the recruitment process.

- **For Job Seekers**: The platform allows users to upload their resumes, receive an in-depth AI-powered analysis and score, get personalized recommendations for skills and courses, practice for interviews with a mock interview simulator, and browse/apply for jobs.
- **For Recruiters/Admins**: The platform provides a secure admin panel to manage job postings, track applicants through the hiring funnel, view analytics on user data and skill trends, and manage user accounts.

---

## 2. Core Technologies

The application is built using Python and leverages several key libraries and frameworks:

- **Web Framework**: `streamlit`
- **AI & NLP**: `google-generativeai`, `nltk`, `spacy`
- **Data Handling & Visualization**: `pandas`, `plotly`, `openpyxl`
- **PDF/Document Processing**: `pdfminer.six`, `pytesseract`, `pdf2image`, `python-docx`, `fpdf2`
- **Database**: `PyMySQL` (for MySQL connection)
- **Authentication**: `bcrypt` (for password hashing)
- **Speech & Audio (for Mock Interviews)**: `pyttsx3`, `SpeechRecognition`, `pyaudio`, `streamlit-webrtc`
- **Testing**: `pytest`

---

## 3. Database Schema

The application uses a MySQL database to store all its data. The schema is defined across several tables:

| Table Name          | Purpose                                                                                             | Key Columns                                                                                                                            |
| ------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `users`             | Stores user login information and roles.                                                            | `id` (PK), `username`, `password` (hashed), `role` ('user' or 'admin')                                                                 |
| `user_data`         | Stores the results of every resume analysis performed by a user. Linked to the `users` table.         | `ID` (PK), `user_id` (FK), `Name`, `Email_ID`, `ai_feedback`, `resume_score`, `Predicted_Field`, `User_level`, `Actual_skills`, etc.      |
| `job_postings`      | Stores job listings created by admins.                                                              | `id` (PK), `title`, `description`, `required_skills`, `min_experience_level`, `status` ('open' or 'closed')                              |
| `job_applications`  | Tracks applications submitted by users for jobs. Links `users` and `job_postings`.                  | `id` (PK), `user_id` (FK), `job_id` (FK), `status` ('applied', 'not_eligible', 'mock_interview_pending', 'shortlisted', 'rejected', etc.) |
| `mock_tests`        | Stores results from skill assessment tests (future feature or part of conversational assessment).   | `id` (PK), `user_id` (FK), `score`, `test_history` (JSON)                                                                              |
| `mock_interviews`   | Stores the results and transcripts of mock interviews.                                              | `id` (PK), `user_id` (FK), `overall_summary`, `interview_history` (JSON)                                                               |
| `notifications`     | Stores system-generated notifications for users (e.g., application status changes).                 | `id` (PK), `user_id` (FK), `message`, `is_read`                                                                                        |

---

## 4. Application Architecture & Workflow

The application follows a modular structure, with different files responsible for specific functionalities.

### Entry Point (`web.py`)

1.  **Initialization**: The app starts by setting up the logger, page configuration, and establishing a database connection via `database.py`.
2.  **Role Selection**: A sidebar prompts the user to select a role: "Normal User" or "Admin".
3.  **Routing**:
    - If "Normal User" is selected, the app checks for a logged-in user. If not logged in, it displays the login/registration forms (`auth.py`). If logged in, it passes control to `user_page.py`.
    - If "Admin" is selected, it passes control to `admin_page.py`.

### Authentication (`auth.py`)

-   **Registration**: Hashes the user's password using `bcrypt` and stores the new user in the `users` table.
-   **Login**: Compares the provided password with the stored hash. On success, the `user_id` is stored in the Streamlit session state (`st.session_state`), marking the user as logged in.

### AI Integration (`ai_utils.py`)

This module is the core of the AI functionality. It communicates with the Google Generative AI API to:
-   `generate_resume_analysis`: Takes raw resume text and an optional job description to produce a detailed analysis, including a score, skill breakdown, and improvement suggestions.
-   `generate_job_description`: Takes a job title and generates a full job description and a list of required skills for the admin panel.
-   `generate_next_question` / `generate_updated_analysis`: Powers the conversational assessment by generating follow-up questions and refining the resume analysis based on user answers.

---

## 5. User Roles & Feature Workflows

### A. Job Seeker (Normal User) Workflow

The entire user journey is handled within `user_page.py`.

1.  **Resume Analysis**:
    - The user uploads a PDF resume.
    - The system extracts the text (`file_utils.py`), sends it to the AI for analysis (`ai_utils.py`), and saves the results to the `user_data` table (`database.py`).
    - The results are displayed on the screen, broken down into sections like Basic Info, Skills, AI Feedback, and Course Recommendations (`ui.py`).
2.  **Conversational Assessment**:
    - After the initial analysis, the user can start an interactive assessment.
    - The AI asks a series of multiple-choice questions to better understand the user's skills and experience.
    - Upon completion, an updated, more detailed analysis is generated and displayed.
3.  **Dashboard**:
    - **My Dashboard** is a tabbed interface for the user to manage their activity.
    - **Past Analyses**: View history of all previous resume uploads and their scores.
    - **Job Opportunities**: A job board (`display_job_board`) where users can view and apply for jobs posted by admins. When a user applies, the system checks their latest resume analysis against the job's requirements to determine if they are eligible for a mock interview.
    - **My Progress**: View charts (`display_progress_charts`) showing how their resume score has improved over time.
    - **Past Interview Analysis**: Review feedback from completed mock interviews.
4.  **Mock Interview Prep (`interview_prep.py`)**:
    - Users can start a mock interview for a specific job they applied for or a general one.
    - The system uses text-to-speech (`pyttsx3`) to ask a question, and speech-to-text (`SpeechRecognition`) to capture the user's answer.
    - At the end of the session, the AI provides an overall performance summary, which is saved to the `mock_interviews` table.

### B. Recruiter (Admin) Workflow

The admin journey starts in `admin_page.py` and utilizes `admin_panel.py` for detailed logic.

1.  **Login**: The admin logs in with credentials stored securely in `secrets.toml`.
2.  **Admin Dashboard**:
    - This is the main landing page, showing high-level analytics.
    - **Data Visualizations**: Interactive charts (from `plotly`) display the distribution of candidate experience levels, popular predicted career fields, in-demand skills from job postings, and user activity over time.
    - **User Data Table**: A searchable and filterable table of all resume analyses performed by users. The admin can download this data as a PDF or Excel file.
    - **Database Actions**: Admins have access to high-risk functions to "Delete All Data" or "Reset Database", both protected by confirmation steps.
3.  **Interview Funnel (Applicant Tracking System)**:
    - Handled by `handle_admin_panel` in `admin_panel.py`.
    - **Job Management**: Admins can create new job postings (with AI assistance to generate descriptions), and then open, close, or delete existing ones.
    - **Applicant Viewing**: For each job, admins can view a list of all applicants. The view includes the applicant's resume score, AI summary, and mock interview feedback.
    - **Status Updates**: Based on the applicant's data, the admin can move them through the hiring pipeline by changing their status (e.g., from 'Mock Interview Passed' to 'Shortlisted' or 'Rejected'). This triggers a notification for the user.
4.  **User Management**:
    - Handled by `handle_user_management` in `admin_panel.py`.
    - Admins can view a list of all registered users and have the ability to permanently delete a user and all their associated data from the database.
