# TalentLink | AI-Driven Smart Career Ecosystem

**TalentLink** is an advanced, cyberpunk-aesthetic career platform that leverages Large Language Models (Google Gemini) and Vector Embeddings to revolutionize the recruitment lifecycle. From autonomous AI interviews to strategic career roadmaps, TalentLink bridges the gap between human potential and organizational needs.

![TalentLink Badge](https://img.shields.io/badge/TalentLink-Neural_Active-blue?style=for-the-badge&logo=google-gemini) ![Status](https://img.shields.io/badge/System-Online-success?style=for-the-badge)

---

## 🌌 Core Philosophy
TalentLink treats careers as dynamic trajectories rather than static documents. It operates on a hierarchical ecosystem:
- **Societies:** High-level networks of industry collectives.
- **Organizations:** Specific entities (Companies, Institutes) within a Society.
- **Recruiters:** Verified employees who manage talent acquisition for their Organizations.
- **Users:** Candidates navigating their career path through AI-guided insights.

---

## 🚀 Key Modules

### 🤖 AI Autonomous Recruitment (The Recruiter Portal)
*Formerly "Employer Portal", now fully refactored for modern scale.*
- **AI Round Assignment:** Recruiters can assign specific AI Agents (Aura AI, Neuro-Scribe, The Oracle) to conduct 1st-round interviews automatically.
- **Tone Customization:** Set the interviewer's personality—from "Encouraging" to "High-Pressure/Clinical".
- **AI Scout Reports:** Detailed feedback reports generated post-interview, including aggregate scores, strengths, and probing questions for the 2nd round.
- **Semantic Talent Search:** Find candidates using natural language queries powered by ChromaDB vector search.

### 🧠 Candidate Growth Engine
- **Dream Job Reality Bridge:** Visual gap analysis that builds a step-by-step roadmap from your current resume to your target role.
- **Live Interview Coach:** Real-time speech-to-text analysis during mock sessions with sentiment and technical keyword tracking.
- **Smart Resume Analysis:** Predicts your best-fit industry, seniority level, and "Market Value" based on semantic depth.

### 🛡️ System Intelligence (Admin Command Center)
- **Homeostasis & Self-Healing:** A proactive system that monitors route health and can "quarantine" unstable neural paths.
- **Identity Control:** Manage the verification of Recruiters and Organizations within the Society.
- **Market Intel:** Real-time analytics on skill supply and demand clusters.

---

## 🛠️ Tech Stack
- **AI Engine:** Google Gemini 2.5 Flash-Lite
- **Vector Engine:** ChromaDB (for semantic matching)
- **Backend:** Flask, SQLAlchemy, Flask-SocketIO (Real-time duplex communication)
- **Frontend:** HTML5/CSS3 (Glassmorphism), Three.js (3D visuals), Feather Icons
- **Database:** SQLite (Dev) / MySQL (Prod)
- **Audio:** Web Speech API

---

## 📦 Project Setup

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key (obtain from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
```bash
# Clone the repository
git clone <repo_url>
cd TalentLink

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_api_key_here

# Admin Initial Credentials
ADMIN_EMAIL=admin@talentlink.ai
ADMIN_PASSWORD=your_password
```

### 4. Database Initialization
```bash
# Apply migrations and create tables
flask db upgrade

# Optional: Run the reset script if starting fresh
python -c "from app import create_app; from app.extensions import db; app=create_app(); with app.app_context(): db.create_all()"
```

### 5. Launch the Neural Link
```bash
python run.py
```
The system will be accessible at `http://127.0.0.1:5000`.

---

## 📂 Project Structure
```text
TalentLink/
├── app/
│   ├── auth/           # Identity & Access Management
│   ├── recruiter/      # Recruiter Dashboard & Job Management
│   ├── admin/          # Command Center & System Oversight
│   ├── user/           # Candidate Dashboard & Career Tools
│   ├── services/       # Core Logic (AI, Interview, Gamification)
│   ├── utils/          # AI Helpers, Vector DB, Homeostasis
│   ├── models.py       # SQLAlchemy Ecosystem Models
│   └── templates/      # Glassmorphic UI Components
├── chroma_db/          # Vector Embeddings
├── tests/              # Validation Protocols
├── run.py              # System Entry Point (with Reloader)
└── requirements.txt    # Neural Dependencies
```

---
*TalentLink © 2026. Empowering Human Potential through Synthetic Intelligence.*
