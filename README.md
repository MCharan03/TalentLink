# TalentLink | Smart Career Platform

**TalentLink** is a comprehensive **Smart Career Platform**. Powered by Google Gemini and an advanced resume analysis engine, TalentLink bridges the gap between human potential and market opportunity with glassmorphic elegance and real-time intelligence.

![TalentLink Badge](https://img.shields.io/badge/TalentLink-Active-blue?style=for-the-badge&logo=google-gemini) ![Status](https://img.shields.io/badge/System-Online-success?style=for-the-badge)

## 🌌 The Vision
TalentLink treats your career as a living, breathing entity. It doesn't just "analyze" your resume; it understands your trajectory. 
- **For Candidates:** It acts as a 24/7 Career Agent, providing real-time interview coaching, resume optimization, and strategic "Bridge" roadmaps to your dream job.
- **For Recruiters:** It uses semantic vector search to find candidates who *actually* fit the role, beyond just keyword matching.

## 🚀 Key Features

### 🧠 AI Assistant
- **Context Aware:** The assistant understands your resume context and can help with specific queries.
- **Persistent Memory:** Remembers your skills, goals, and previous conversations.

### 🎯 Strategic Career Tools
- **Dream Job Reality Bridge:** A visual gap-analysis tool. Tell it you want to be a "Senior Architect at Google," and it builds a step-by-step roadmap to get you there from your current state.
- **Live Interview Coach:** Real-time speech recognition analyzes your interview answers and provides a detailed "Report Card" on sentiment, confidence, and technical keyword usage.
- **Smart Resume Analysis:** Deep semantic analysis of your CV against millions of data points to predict your best-fit industry and seniority level.

### 🛡️ For The Enterprise
- **Market Intelligence:** Aggregates real-time job data to show supply/demand trends for specific skills.
- **Neural Matching:** Matches candidates to jobs using vector embeddings for superior relevance.
- **Command Center:** A glassmorphic admin dashboard for full system oversight.

## 🛠️ Tech Stack
- **AI Engine:** Google Gemini 2.5 Flash-Lite (Context-Aware)
- **Backend:** Flask, SQLAlchemy, Flask-SocketIO (Real-time)
- **Database:** SQLite / MySQL + **ChromaDB (Vector Search)**
- **Frontend:** Bootstrap 5, Glassmorphism CSS, Three.js (Visuals), Vanilla Tilt
- **Audio:** Web Speech API (Recognition & Synthesis)

## 📦 Quick Start

### 1. Clone & Setup
```bash
git clone <repo_url>
cd TalentLink
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your keys:
```env
GEMINI_API_KEY=your_gemini_key_here
SECRET_KEY=super_secret_key
```

### 3. Launch
```bash
# Initialize Database
flask db upgrade

# Run System
python run.py
```
Access the neural link at `http://127.0.0.1:5000`.

---
*TalentLink © 2026. Empowering Human Potential.*