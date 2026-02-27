from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import current_user
import io
import csv
from datetime import datetime

from . import admin
from .forms import JobPostingForm
from ..extensions import db
from ..models import JobPosting, JobApplication, User, UserData, MockTest, MockInterview, Notification, SystemSetting, Quest, Organization, RecruiterProfile
from ..utils.ai_utils import generate_job_description, analyze_market_trends
from ..decorators import admin_required
import threading


@admin.route('/recruiter_approvals')
@admin_required
def recruiter_approvals():
    pending_recruiters = RecruiterProfile.query.filter_by(is_verified=False).all()
    return render_template('admin/recruiter_approvals.html', pending_recruiters=pending_recruiters)

@admin.route('/approve_recruiter/<int:profile_id>', methods=['POST'])
@admin_required
def approve_recruiter(profile_id):
    profile = RecruiterProfile.query.get_or_404(profile_id)
    user = profile.user
    
    # 1. Generate Credentials
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    user.set_password(password)
    user.role = 'recruiter' # Ensure role is set
    profile.is_verified = True
    db.session.commit()
    
    # 2. Send Email
    try:
        from ..utils.email_utils import send_email
        send_email(
            to=user.email,
            subject="Your Recruiter Account is Approved - SRA",
            template=None,
            category='partners',
            body=f"""Hello {user.username},

Your request to join as a Recruiter for {profile.organization.name} has been approved!

Here are your login credentials:
Email: {user.email}
Password: {password}

Please login and change your password immediately.

Login here: {url_for('auth.login', _external=True)}

Welcome aboard,
SRA Admin Team"""
        )
        flash(f'Recruiter {user.username} approved and credentials sent.', 'success')
    except Exception as e:
        flash(f'Recruiter approved but email failed: {e}', 'warning')
        
    return redirect(url_for('admin.recruiter_approvals'))

@admin.route('/reject_recruiter/<int:profile_id>', methods=['POST'])
@admin_required
def reject_recruiter(profile_id):
    profile = RecruiterProfile.query.get_or_404(profile_id)
    user = profile.user
    
    # Send Rejection Email first
    try:
        from ..utils.email_utils import send_email
        send_email(
            to=user.email,
            subject="Update on your Recruiter Request - SRA",
            template=None,
            category='partners',
            body=f"""Hello {user.username},

Thank you for your interest in joining SRA as a Recruiter.
After reviewing your request, we are unable to approve your account at this time.

If you believe this is an error, please contact support.

Regards,
SRA Admin Team"""
        )
    except Exception as e:
        print(f"Rejection email failed: {e}")

    # Delete Data
    db.session.delete(profile)
    db.session.delete(user) 
    db.session.commit()
    
    flash(f'Recruiter request for {user.email} rejected and deleted.', 'info')
    return redirect(url_for('admin.recruiter_approvals'))

@admin.route('/controls')
@admin_required
def controls():
    settings = SystemSetting.query.all()
    # Convert list to dict for easier template access if needed, or pass as list
    return render_template('admin/controls.html', settings=settings)

@admin.route('/api/update_setting', methods=['POST'])
@admin_required
def update_setting():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Setting {key} updated.'})
    else:
        return jsonify({'status': 'error', 'message': 'Setting not found.'}), 404

@admin.route('/api/reindex_vectors', methods=['POST'])
@admin_required
def reindex_vectors():
    try:
        from ..utils.vector_utils import add_job_to_vector_db, add_resume_to_vector_db
        
        # Re-index Jobs
        jobs = JobPosting.query.all()
        for job in jobs:
            add_job_to_vector_db(job.id, job.title, job.description)
            
        # Re-index Resumes (Latest for each user)
        # Group by user to get latest
        # Simplified: Just iterate all UserData and let Chroma update (last write wins usually, but we want latest by date)
        # Better: get latest per user
        latest_data = UserData.query.order_by(UserData.uploaded_at.asc()).all() 
        # Iterate all, last one overwrites previous in vector db if same ID used
        for ud in latest_data:
            if ud.analysis_result:
                skills = ud.analysis_result.get('actual_skills', [])
                # Resume text extraction might be slow if we do it here. 
                # Ideally, store extracted text in DB. 
                # For this prototype, we'll skip text extraction and just use skills for now 
                # OR assume we can't fully re-index text without file access. 
                # Let's just index skills as a placeholder for the "text" field to be safe.
                # In real app: read file from disk.
                try:
                    from ..utils.file_utils import extract_text_from_pdf
                    import os
                    path = os.path.join(current_app.config['UPLOAD_FOLDER'], ud.resume_path)
                    if os.path.exists(path):
                        text = extract_text_from_pdf(path)
                        add_resume_to_vector_db(ud.user_id, text, skills)
                except:
                    pass
        
        return jsonify({'status': 'success', 'message': 'Vector DB re-indexed.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin.route('/create_quest', methods=['POST'])
@admin_required
def create_quest():
    title = request.form.get('title')
    description = request.form.get('description')
    xp = request.form.get('xp')
    criteria_type = request.form.get('criteria_type') # e.g. 'manual', 'login', 'upload'
    
    quest = Quest(
        title=title,
        description=description,
        xp_reward=int(xp),
        criteria={'type': criteria_type}
    )
    db.session.add(quest)
    db.session.commit()
    flash('New Quest Deployed to Universe.', 'success')
    return redirect(url_for('admin.controls'))

@admin.route('/market_intelligence')
@admin_required
def market_intelligence():
    # 1. Aggregate Job Data (Demand)
    # Get last 50 jobs to keep prompt size manageable
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(50).all()
    job_text = "\n".join([f"- {j.title}: {j.description[:200]}..." for j in jobs])
    
    # 2. Aggregate User Data (Supply)
    all_users_data = UserData.query.all()
    from collections import Counter
    all_skills = []
    for ud in all_users_data:
        if ud.analysis_result:
            all_skills.extend(ud.analysis_result.get('actual_skills', []))
    
    skill_counts = Counter(all_skills).most_common(50)
    skills_summary = ", ".join([f"{s[0]} ({s[1]} users)" for s in skill_counts])
    
    # 3. AI Analysis
    # In a real app, cache this result as it's expensive
    analysis = analyze_market_trends(job_text, skills_summary)
    
    if not analysis:
        analysis = {
            "undersupplied_skills": [],
            "oversupplied_skills": [],
            "emerging_trends": ["Data Unavailable"],
            "strategic_advice": "Could not generate analysis. Please ensure there is enough data.",
            "market_health_score": 0
        }
    
    return render_template('admin/market_intelligence.html', analysis=analysis)

@admin.route('/dashboard')
@admin_required
def dashboard():
    # Fetch user data for the table
    user_data = UserData.query.order_by(UserData.uploaded_at.desc()).all()
    
    # --- Analytics Logic ---
    from collections import Counter
    
    fields = []
    levels = []
    all_skills = []
    
    for entry in user_data:
        res = entry.analysis_result
        if res:
            fields.append(res.get('predicted_field', 'Unknown'))
            levels.append(res.get('experience_level', 'Unknown'))
            skills = res.get('actual_skills', [])
            if isinstance(skills, list):
                all_skills.extend([s.lower() for s in skills])

    # Counter objects
    field_counts = dict(Counter(fields))
    level_counts = dict(Counter(levels))
    skill_counts = dict(Counter(all_skills).most_common(10)) # Top 10 skills

    # Activity Timeline
    from sqlalchemy import func
    analysis_dates = db.session.query(func.date(UserData.uploaded_at), func.count(UserData.id)).group_by(func.date(UserData.uploaded_at)).all()
    
    engagement_dates = []
    for d in analysis_dates:
        date_val = d[0]
        if isinstance(date_val, str):
            engagement_dates.append(date_val)
        elif date_val:
             engagement_dates.append(date_val.strftime('%Y-%m-%d'))
        else:
            engagement_dates.append('')
            
    analysis_counts = [d[1] for d in analysis_dates]

    form = JobPostingForm()
    
    # Fetch settings for inline controls
    all_settings = SystemSetting.query.all()
    settings_dict = {s.key: s.value for s in all_settings}

    return render_template('admin/dashboard.html', 
                           user_data=user_data,
                           engagement_dates=engagement_dates,
                           analysis_counts=analysis_counts,
                           field_counts=field_counts,
                           level_counts=level_counts,
                           skill_counts=skill_counts,
                           form=form,
                           settings=settings_dict)

@admin.route('/actions')
@admin_required
def actions():
    return render_template('admin/actions.html')

@admin.route('/interview_funnel')
@admin_required
def interview_funnel():
    jobs = JobPosting.query.all()
    form = JobPostingForm()
    return render_template('admin/interview_funnel.html', jobs=jobs, form=form)

@admin.route('/user_management')
@admin_required
def user_management():
    users = User.query.all()
    return render_template('admin/user_management.html', all_users=users)

@admin.route('/update_user_role/<int:user_id>', methods=['POST'])
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin.user_management'))
        
    if new_role in ['user', 'recruiter', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'User {user.username} role updated to {new_role}.', 'success')
    else:
        flash('Invalid role selected.', 'danger')
        
    return redirect(url_for('admin.user_management'))

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    import time
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] DEBUG: START Attempting to delete user_id: {user_id}", flush=True)
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        print(f"[{timestamp}] DEBUG: User {user_id} tried to delete themselves. ABORTING.", flush=True)
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.user_management'))
        
    try:
        print(f"[{timestamp}] DEBUG: Manual cleanup of related data for {user.username}...", flush=True)
        # Manually delete dependencies if they are blocking
        # These will handle cases where cascade might be stuck or missing
        Notification.query.filter_by(user_id=user.id).delete()
        JobApplication.query.filter_by(user_id=user.id).delete()
        UserData.query.filter_by(user_id=user.id).delete()
        MockTest.query.filter_by(user_id=user.id).delete()
        MockInterview.query.filter_by(user_id=user.id).delete()
        
        from ..models import UserQuest, UserXP, CareerForecast
        UserQuest.query.filter_by(user_id=user.id).delete()
        UserXP.query.filter_by(user_id=user.id).delete()
        CareerForecast.query.filter_by(user_id=user.id).delete()
        
        # Recruiter Profile
        if user.recruiter_profile:
            db.session.delete(user.recruiter_profile)
        
        print(f"[{timestamp}] DEBUG: Deleting main user record...", flush=True)
        db.session.delete(user)
        db.session.commit()
        print(f"[{timestamp}] DEBUG: SUCCESS. User {user_id} deleted.", flush=True)
        flash(f'User {user.username} deleted.', 'success')
    except Exception as e:
        print(f"[{timestamp}] DEBUG: ERROR during delete: {e}", flush=True)
        db.session.rollback()
        flash(f'Error deleting user: {e}', 'danger')
        
    return redirect(url_for('admin.user_management'))

@admin.route('/send_user_notification/<int:user_id>', methods=['POST'])
@admin_required
def send_user_notification(user_id):
    user = User.query.get_or_404(user_id)
    message = request.form.get('message')
    
    if message:
        notif = Notification(user_id=user.id, message=f"ADMIN: {message}")
        db.session.add(notif)
        db.session.commit()
        flash(f'Notification sent to {user.username}.', 'success')
    else:
        flash('Message cannot be empty.', 'warning')
        
    return redirect(url_for('admin.user_management'))

@admin.route('/reset_db', methods=['POST'])
@admin_required
def reset_db():
    if request.form.get('confirm') == 'yes':
        try:
            Notification.query.delete()
            JobApplication.query.delete()
            JobPosting.query.delete()
            UserData.query.delete()
            MockTest.query.delete()
            MockInterview.query.delete()
            # Be careful not to delete the current admin user if possible, or force logout
            # Here we delete all non-admin users
            User.query.filter(User.role != 'admin').delete()
            db.session.commit()
            flash('Database has been reset successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error resetting database: {e}', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin.route('/export_data')
@admin_required
def export_data():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['User ID', 'Username', 'Email', 'Role', 'Date Joined'])
    users = User.query.all()
    for user in users:
        cw.writerow([user.id, user.username, user.email, user.role, user.created_at])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@admin.route('/create_job', methods=['POST'])
@admin_required
def create_job():
    form = JobPostingForm()
    if form.validate_on_submit():
        job = JobPosting(title=form.title.data, description=form.description.data, created_by=current_user.id)
        db.session.add(job)
        db.session.commit()
        # Add to Vector DB (non-blocking to avoid UI "stuck" if Chroma is slow/locked)
        def _index_job(job_id, title, description):
            try:
                from ..utils.vector_utils import add_job_to_vector_db
                add_job_to_vector_db(job_id, title, description)
            except Exception as e:
                print(f"Background indexing failed for job {job_id}: {e}")

        threading.Thread(
            target=_index_job,
            args=(job.id, job.title, job.description),
            daemon=True
        ).start()
        
        flash('Job posting created. Indexing pipeline in background…', 'success')
    return redirect(url_for('admin.interview_funnel'))

@admin.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@admin_required
def edit_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    form = JobPostingForm(obj=job)
    
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        db.session.commit()
        
        # Update Vector DB (non-blocking)
        def _index_job(job_id, title, description):
            try:
                from ..utils.vector_utils import add_job_to_vector_db
                add_job_to_vector_db(job_id, title, description)
            except Exception as e:
                print(f"Background indexing failed for job {job_id}: {e}")

        threading.Thread(
            target=_index_job,
            args=(job.id, job.title, job.description),
            daemon=True
        ).start()
        
        flash('Job posting updated.', 'success')
        return redirect(url_for('admin.interview_funnel'))
        
    return render_template('admin/edit_job.html', form=form, job=job)

from ..decorators import admin_required, recruiter_required

@admin.route('/api/generate_job_desc', methods=['POST'])
@recruiter_required
def generate_job_desc_api():
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # generate_job_description returns a string
    description = generate_job_description(title) 
    
    return jsonify({'description': description})

@admin.route('/delete_job/<int:job_id>', methods=['POST'])
@admin_required
def delete_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    # Optional: Delete associated applications? 
    # SQLAlchemy cascade might handle this if configured, else manual delete
    db.session.delete(job)
    db.session.commit()
    flash('Job posting deleted.', 'success')
    return redirect(url_for('admin.interview_funnel'))

@admin.route('/job_applicants/<int:job_id>')
@admin_required
def job_applicants(job_id):
    job = JobPosting.query.get_or_404(job_id)
    applications = JobApplication.query.filter_by(job_id=job_id).order_by(JobApplication.applied_at.desc()).all()
    
    # Collect resume scores for these applicants
    applicant_data = []
    for app in applications:
        # Find the latest resume analysis for this user *before* or *at* application time
        # Or just the latest general analysis
        # For simplicity, let's grab the user's latest analysis
        latest_analysis = UserData.query.filter_by(user_id=app.user_id).order_by(UserData.uploaded_at.desc()).first()
        score = latest_analysis.analysis_result.get('resume_score', 'N/A') if latest_analysis and latest_analysis.analysis_result else 'N/A'
        
        applicant_data.append({
            'application': app,
            'user': app.user,
            'score': score
        })
        
    return render_template('admin/job_applicants.html', job=job, applicant_data=applicant_data)

@admin.route('/update_application_status/<int:app_id>/<status>')
@admin_required
def update_application_status(app_id, status):
    application = JobApplication.query.get_or_404(app_id)
    valid_statuses = ['submitted', 'shortlisted', 'interviewing', 'rejected', 'hired']
    
    if status not in valid_statuses:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Invalid status'}), 400
        flash('Invalid status update.', 'danger')
        return redirect(url_for('admin.job_applicants', job_id=application.job_id))
    
    application.status = status
    
    # Create notification for the user
    status_msg = {
        'shortlisted': 'You have been shortlisted!',
        'interviewing': 'We would like to invite you for an interview.',
        'rejected': 'Thank you for your interest, but we are moving forward with other candidates.',
        'hired': 'Congratulations! You have been hired.',
        'submitted': 'Your application status has been reset to submitted.'
    }
    
    msg = f"Update on your application for '{application.job.title}': {status_msg.get(status, status)}"
    notification = Notification(user_id=application.user_id, message=msg)
    
    db.session.add(notification)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'new_status': status})
        
    flash(f"Application status updated to {status}.", 'success')
    return redirect(url_for('admin.job_applicants', job_id=application.job_id))

@admin.route('/update_application_notes/<int:app_id>', methods=['POST'])
@admin_required
def update_application_notes(app_id):
    application = JobApplication.query.get_or_404(app_id)
    application.notes = request.form.get('notes')
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
        
    flash('Notes updated.', 'success')
    return redirect(url_for('admin.job_applicants', job_id=application.job_id))

@admin.route('/view_analysis/<int:user_data_id>')
@admin_required
def view_analysis(user_data_id):
    user_data = UserData.query.get_or_404(user_data_id)
    predicted_field = user_data.analysis_result.get('predicted_field', '')
    from ..utils.resource_utils import get_curated_courses
    curated_courses = get_curated_courses(predicted_field)
    
    return render_template('admin/view_analysis.html', 
                           result=user_data.analysis_result, 
                           user_data=user_data,
                           curated_courses=curated_courses)
