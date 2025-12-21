# Smart Resume Screener & Analyzer

## Project Overview

The Smart Resume Screener & Analyzer is a Streamlit-based web application designed to assist both job seekers and recruiters. It leverages AI to provide in-depth resume analysis, offer personalized improvement suggestions, and facilitate mock interviews. For recruiters and administrators, it provides tools for job posting management, applicant tracking, and user data visualization.

## Features

### For Job Seekers (Normal Users)

*   **Resume Analysis:** Upload your resume (PDF) to receive a comprehensive AI-powered analysis.
    *   **Dynamic Feedback:** Get detailed insights into strengths and weaknesses, including suggestions for stronger action verbs and improved formatting.
    *   **Keyword Matching (Dynamic):** Optionally paste a job description to receive a semantic match score and tailored advice on how to align your resume better with specific job requirements.
*   **Personalized Recommendations:** Receive AI-driven recommendations for skills to acquire and courses to take based on your resume and predicted career field.
*   **Mock Interviews:** Practice with AI-generated mock interviews to hone your interviewing skills.
*   **Dashboard:** View past resume analyses, track job applications, review past interview feedback, and monitor your progress over time.
*   **Job Board:** Browse available job opportunities and apply directly through the platform.
*   **Notifications:** Receive in-app notifications regarding your application status.

### For Recruiters/Administrators (Admin Users)

*   **Admin Login:** Secure login to access administrative functionalities.
*   **User Data Dashboard:** View and filter all user data, including resume analyses and progress.
*   **Data Visualizations:** Gain insights from charts showing predicted fields and candidate experience levels.
*   **Job Posting Management:** Create, update, and manage job postings.
*   **Applicant Tracking:** View applicants for specific job postings, manage their status (shortlist, reject), and review their resume analyses and mock interview feedback.
*   **User Management:** View and delete user accounts.

## Installation and Setup

To get the Smart Resume Screener & Analyzer up and running on your local machine, follow these steps:

### Prerequisites

*   **Python 3.8+**
*   **MySQL Database:** Ensure you have a running MySQL server.
*   **Tesseract OCR:** (Optional, but recommended for better PDF text extraction) Install Tesseract OCR engine. For Windows, you might need to set the `TESSERACT_CMD` environment variable or specify the path in `file_utils.py`.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd "Resume Screening"
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

The application uses a `.streamlit/secrets.toml` file for sensitive information like database credentials and API keys. If this file doesn't exist, it will be created automatically with default values upon first run. **You must edit this file with your actual credentials.**

Create or edit `.streamlit/secrets.toml` in your project root:

```toml
[mysql]
host = "localhost"
user = "root"
password = "your_mysql_password"
database = "sra"

[admin]
username = "your_admin_username"
password = "your_admin_password"

[google_ai]
api_key = "YOUR_GEMINI_API_KEY"
```

*   Replace `your_mysql_password`, `your_admin_username`, `your_admin_password`, and `YOUR_GEMINI_API_KEY` with your actual values.
*   Ensure your `secrets.toml` is added to `.gitignore` to prevent it from being committed to version control.

### 5. Database Setup

The application will attempt to set up the necessary database and tables (`sra` database, `users`, `user_data`, `mock_tests`, `mock_interviews`, `job_postings`, `job_applications`, `notifications` tables) on its first run. Ensure your MySQL server is running and accessible with the credentials provided in `secrets.toml`.

### 6. Configure Course and Video Data

The application uses `config.json` for course and video recommendations. This file is automatically created if it doesn't exist. You can modify `config.json` to update or add new courses and video links.

## Usage

To run the Streamlit application, execute the following command in your terminal from the project root directory:

```bash
streamlit run web.py
```

Your browser should automatically open to the Streamlit application. If not, navigate to `http://localhost:8501` (or the address displayed in your terminal).

## Future Enhancements (Deferred Tasks)

*   **Implement Email Notifications:** Integrate an email service to send users email notifications for important updates.
*   **Add a Resume Builder:** Develop a feature that allows users to create and edit their resumes directly within the application, guided by AI suggestions.

