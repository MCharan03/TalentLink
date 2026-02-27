from flask import render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from . import employer
from ..services.employer_service import EmployerService
from ..models import UserData, JobPosting, JobApplication, Notification, db
from ..decorators import employer_required
from ..admin.forms import JobPostingForm # Reusing form

@employer.route('/dashboard')
@employer_required
def dashboard():
    employer_service = EmployerService()
    query = request.args.get('q', '')
    candidates = []
    
    if query:
        candidates = employer_service.search_talent(query)
    
    # Real stats from DB
    active_jobs_count = JobPosting.query.filter_by(created_by=current_user.id).count()
    
    # Total applications across all employer's jobs
    employer_job_ids = [j.id for j in JobPosting.query.filter_by(created_by=current_user.id).all()]
    total_applications = JobApplication.query.filter(JobApplication.job_id.in_(employer_job_ids)).count() if employer_job_ids else 0
    shortlisted_count = JobApplication.query.filter(
        JobApplication.job_id.in_(employer_job_ids),
        JobApplication.status == 'shortlisted'
    ).count() if employer_job_ids else 0
    
    return render_template('employer/dashboard.html', 
                           candidates=candidates, 
                           query=query, 
                           active_jobs_count=active_jobs_count,
                           total_applications=total_applications,
                           shortlisted_count=shortlisted_count)

# --- Job Management ---

@employer.route('/jobs')
@employer_required
def manage_jobs():
    # Show only jobs created by this employer (or all if admin)
    if current_user.role == 'admin':
        jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    else:
        jobs = JobPosting.query.filter_by(created_by=current_user.id).order_by(JobPosting.created_at.desc()).all()
        
    return render_template('employer/manage_jobs.html', jobs=jobs)

@employer.route('/jobs/create', methods=['GET', 'POST'])
@employer_required
def create_job():
    form = JobPostingForm()
    if form.validate_on_submit():
        job = JobPosting(
            title=form.title.data, 
            description=form.description.data, 
            created_by=current_user.id,
            # Associate with company if profile exists
            company_id=current_user.employer_profile.company_id if current_user.employer_profile else None
        )
        db.session.add(job)
        db.session.commit()
        
        # Add to Vector DB
        try:
            from ..utils.vector_utils import add_job_to_vector_db
            add_job_to_vector_db(job.id, job.title, job.description)
        except Exception as e:
            print(f"Vector DB Error: {e}")
            
        flash('Job posting created successfully.', 'success')
        return redirect(url_for('employer.manage_jobs'))
        
    return render_template('employer/job_form.html', form=form, title="Create New Job")

@employer.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
@employer_required
def edit_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    # Security Check
    if current_user.role != 'admin' and job.created_by != current_user.id:
        abort(403)
        
    form = JobPostingForm(obj=job)
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        db.session.commit()
        
        # Update Vector DB
        try:
            from ..utils.vector_utils import add_job_to_vector_db
            add_job_to_vector_db(job.id, job.title, job.description)
        except Exception as e:
            print(f"Vector DB Error: {e}")
            
        flash('Job updated.', 'success')
        return redirect(url_for('employer.manage_jobs'))
        
    return render_template('employer/job_form.html', form=form, title="Edit Job")

@employer.route('/jobs/delete/<int:job_id>', methods=['POST'])
@employer_required
def delete_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    if current_user.role != 'admin' and job.created_by != current_user.id:
        abort(403)
        
    db.session.delete(job)
    db.session.commit()
    flash('Job posting deleted.', 'info')
    return redirect(url_for('employer.manage_jobs'))

@employer.route('/jobs/applicants/<int:job_id>')
@employer_required
def job_applicants(job_id):
    job = JobPosting.query.get_or_404(job_id)
    if current_user.role != 'admin' and job.created_by != current_user.id:
        abort(403)
        
    applications = JobApplication.query.filter_by(job_id=job_id).order_by(JobApplication.applied_at.desc()).all()
    
    applicant_data = []
    for app in applications:
        # Get latest resume score for context
        latest_analysis = UserData.query.filter_by(user_id=app.user_id).order_by(UserData.uploaded_at.desc()).first()
        score = latest_analysis.analysis_result.get('resume_score', 'N/A') if latest_analysis and latest_analysis.analysis_result else 'N/A'
        
        applicant_data.append({
            'application': app,
            'user': app.user,
            'score': score
        })
        
    return render_template('employer/job_applicants.html', job=job, applicant_data=applicant_data)

@employer.route('/application/status/<int:app_id>/<status>')
@employer_required
def update_application_status(app_id, status):
    application = JobApplication.query.get_or_404(app_id)
    # Check ownership of the job this app belongs to
    job = JobPosting.query.get(application.job_id)
    if current_user.role != 'admin' and job.created_by != current_user.id:
        abort(403)
        
    valid_statuses = ['submitted', 'shortlisted', 'interviewing', 'rejected', 'hired']
    if status in valid_statuses:
        application.status = status
        
        # Notify Candidate
        msg = f"Update on your application for '{job.title}': {status.capitalize()}"
        notif = Notification(user_id=application.user_id, message=msg)
        db.session.add(notif)
        db.session.commit()
        
        # Send Email
        try:
            from ..utils.email_utils import send_email
            send_email(
                to=application.user.email,
                subject=f"Application Update: {job.title}",
                template=None,
                category='notifications',
                body=f"Hello {application.user.username},\n\nYour application status for {job.title} has been updated to: {status.upper()}.\n\nCheck your dashboard for details.\n\nBest,\nRecruiting Team"
            )
        except:
            pass
            
        flash(f'Applicant status updated to {status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(url_for('employer.job_applicants', job_id=job.id))

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
