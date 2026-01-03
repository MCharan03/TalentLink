from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import employer
from ..services.employer_service import EmployerService
from ..models import UserData, JobPosting

@employer.route('/dashboard')
@login_required
def dashboard():
    # Only allow employers (role check needed, assuming 'employer' role exists or admin)
    # For prototype, we'll allow anyone with 'employer' or 'admin' role
    if current_user.role not in ['employer', 'admin']:
        flash('Access restricted to employers.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    employer_service = EmployerService()
    query = request.args.get('q', '')
    candidates = []
    
    if query:
        candidates = employer_service.search_talent(query)
    
    return render_template('employer/dashboard.html', candidates=candidates, query=query)

@employer.route('/candidate/<int:user_id>')
@login_required
def candidate_profile(user_id):
    if current_user.role not in ['employer', 'admin']:
        flash('Access restricted.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # Get candidate data
    user_data = UserData.query.filter_by(user_id=user_id).order_by(UserData.uploaded_at.desc()).first()
    if not user_data:
        flash('Candidate profile not available.', 'warning')
        return redirect(url_for('employer.dashboard'))
        
    employer_service = EmployerService()
    # Mocking a job description for the "Insight" context - in real app, select a job
    # For now, we'll use a generic query context or just the user's predicted field
    job_context = request.args.get('job_context', f"A role in {user_data.analysis_result.get('predicted_field', 'Tech')}")
    
    insight = employer_service.get_candidate_insight(user_id, job_context)
    
    return render_template('employer/candidate_profile.html', 
                           candidate=user_data.user, 
                           profile=user_data.analysis_result,
                           insight=insight)
