from flask import jsonify, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from . import api
from ..models import User, UserData, MockTest, MockInterview, SkillFitAssessment, UserXP, UserQuest, ExternalApplication, JobApplication, JobPosting
from ..extensions import db, bcrypt, csrf
import json

@api.route('/auth/login', methods=['POST'])
@csrf.exempt
def mobile_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        login_user(user, remember=True)
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@api.route('/auth/logout', methods=['POST'])
@csrf.exempt
@login_required
def mobile_logout():
    logout_user()
    return jsonify({'success': True})

@api.route('/dashboard', methods=['GET'])
@csrf.exempt
@login_required
def mobile_dashboard():
    xp_profile = UserXP.query.filter_by(user_id=current_user.id).first()
    if not xp_profile:
        xp_profile = UserXP(user_id=current_user.id)
        db.session.add(xp_profile)
        db.session.commit()

    active_quests = UserQuest.query.filter_by(user_id=current_user.id, status='in_progress').all()
    applications = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.applied_at.desc()).limit(10).all()
    external_apps = ExternalApplication.query.filter_by(user_id=current_user.id).order_by(ExternalApplication.applied_at.desc()).limit(10).all()
    analyses = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).limit(10).all()

    return jsonify({
        'success': True,
        'user': {
            'username': current_user.username,
            'email': current_user.email,
            'xp': xp_profile.total_xp,
            'level': xp_profile.level,
            'energy': xp_profile.energy
        },
        'analyses': [{
            'id': a.id,
            'uploaded_at': a.uploaded_at.isoformat(),
            'score': a.analysis_result.get('resume_score', 0) if a.analysis_result else 0
        } for a in analyses],
        'applications': [{
            'id': app.id,
            'job_title': app.job.title,
            'status': app.status,
            'applied_at': app.applied_at.isoformat()
        } for app in applications],
        'external_apps': [{
            'id': e.id,
            'company': e.company_name,
            'title': e.job_title,
            'status': e.status
        } for e in external_apps],
        'active_quests': [{
            'id': q.id,
            'title': q.quest.title,
            'progress': q.progress
        } for q in active_quests]
    })


@api.route('/interview/start', methods=['POST'])
@csrf.exempt
@login_required
def start_mobile_interview():
    data = request.get_json()
    job_role = data.get('job_role', 'Software Engineer')
    
    # Initialize a new interview
    interview = MockInterview(
        user_id=current_user.id,
        job_role=job_role,
        chat_history=[{"role": "system", "content": f"You are an AI interviewer for a {job_role} position. Start the interview."}]
    )
    db.session.add(interview)
    db.session.commit()
    
    # Generate first question
    from ..utils.ai_utils import _call_gemini
    prompt = f"You are an AI interviewer for a {job_role} role. Ask the first technical or behavioral question to the candidate."
    first_question = _call_gemini(prompt)
    
    interview.chat_history = interview.chat_history + [{"role": "assistant", "content": first_question}]
    db.session.commit()
    
    return jsonify({
        'success': True,
        'interview_id': interview.id,
        'message': first_question
    })

@api.route('/interview/message', methods=['POST'])
@csrf.exempt
@login_required
def mobile_interview_message():
    data = request.get_json()
    interview_id = data.get('interview_id')
    user_message = data.get('message')
    
    if not interview_id or not user_message:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    interview = MockInterview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id:
        return jsonify({'success': False}), 403
        
    # Append user message
    history = list(interview.chat_history)
    history.append({"role": "user", "content": user_message})
    
    # Generate AI response
    from ..utils.ai_utils import _call_gemini
    # Convert history to prompt context
    context = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
    prompt = f"The candidate just said: '{user_message}'. Respond as the interviewer. Keep it concise. Ask the next question or give brief feedback."
    
    ai_response = _call_gemini(f"{context}\\n\\n{prompt}")
    
    history.append({"role": "assistant", "content": ai_response})
    interview.chat_history = history
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': ai_response
    })

@api.route('/jobs', methods=['GET'])
@csrf.exempt
@login_required
def get_jobs():
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    applied_job_ids = [app.job_id for app in current_user.applications]
    
    return jsonify({
        'success': True,
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'description': job.description,
            'salary_range': job.salary_range,
            'requirements': job.requirements,
            'is_applied': job.id in applied_job_ids
        } for job in jobs]
    })

@api.route('/jobs/apply/<int:job_id>', methods=['POST'])
@csrf.exempt
@login_required
def apply_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if already applied
    existing_app = JobApplication.query.filter_by(user_id=current_user.id, job_id=job.id).first()
    if existing_app:
        return jsonify({'success': False, 'message': 'Already applied to this job.'})
        
    application = JobApplication(
        user_id=current_user.id,
        job_id=job.id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Successfully applied!'})
