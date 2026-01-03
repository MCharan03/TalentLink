import os
import json
from flask import render_template, redirect, url_for, flash, request, send_file, current_app, jsonify, send_from_directory, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import user
from .forms import ResumeAnalysisForm, MockTestForm, ResumeBuilderForm, LinkedInBuilderForm, ProfileForm, ChangePasswordForm
from ..extensions import db, socketio
from ..models import UserData, MockTest, JobPosting, JobApplication, Notification, MockInterview, User
from ..utils.ai_utils import (
    analyze_resume,
    generate_next_assessment_question,
    generate_updated_analysis,
    generate_linkedin_content,
    optimize_linkedin_profile,
    get_interview_question,
    generate_cover_letter,
    generate_mock_test,
    generate_professional_summary,
    refine_experience_points,
    tailor_resume_to_job,
    simulate_ats_parsing
)
from ..utils.file_utils import extract_text_from_pdf, get_pdf_page_count
from ..utils.report_utils import generate_resume_pdf, generate_pdf_report, generate_docx_report, generate_resume_pdf_from_profile
from ..utils.github_utils import analyze_github_profile
from ..utils.vector_utils import search_jobs_by_resume, add_resume_to_vector_db
from ..utils.gamification import award_xp, check_quest_progress
from ..models import GitHubProfile, UserXP, Quest, UserQuest
from flask_socketio import emit
import time
from datetime import datetime
import io

# ... existing routes ...

@user.route('/github_audit', methods=['GET', 'POST'])
@login_required
def github_audit():
    if request.method == 'POST':
        username = request.form.get('github_username')
        if not username:
            flash('Please enter a GitHub username.', 'danger')
            return redirect(url_for('user.github_audit'))
            
        try:
            analysis = analyze_github_profile(username)
            if 'error' in analysis:
                flash(analysis['error'], 'danger')
                return redirect(url_for('user.github_audit'))
            
            # Save or Update Profile
            profile = GitHubProfile.query.filter_by(user_id=current_user.id).first()
            if not profile:
                profile = GitHubProfile(user_id=current_user.id)
                
            profile.username = username
            profile.repo_analysis = analysis
            profile.last_scanned = datetime.utcnow()
            
            db.session.add(profile)
            db.session.commit()
            
            # Gamification
            award_xp(current_user, 75, "GitHub Portfolio Audit")
            check_quest_progress(current_user, "github_audit")
            
            flash('GitHub Audit Completed!', 'success')
            return redirect(url_for('user.github_report'))
            
        except Exception as e:
            current_app.logger.error(f"GitHub Audit Error: {e}")
            flash('An error occurred during analysis.', 'danger')
            return redirect(url_for('user.github_audit'))
            
    return render_template('user/github_audit.html')

@user.route('/github_report')
@login_required
def github_report():
    profile = GitHubProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('No audit found. Please run an audit first.', 'warning')
        return redirect(url_for('user.github_audit'))
    return render_template('user/github_report.html', profile=profile)

@user.route('/tailor_resume/<int:job_id>')
@login_required
def tailor_resume(job_id):
    job = JobPosting.query.get_or_404(job_id)
    
    # Get user's latest uploaded resume
    latest_resume = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
    
    if not latest_resume:
        flash('Please upload a base resume first (via Analysis) to use this feature.', 'warning')
        return redirect(url_for('user.resume_analysis'))

    try:
        # Extract text from the existing PDF
        resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_resume.resume_path)
        resume_text = extract_text_from_pdf(resume_path)
        
        # Call AI to tailor it
        tailored_data = tailor_resume_to_job(resume_text, job.description)
        
        if not tailored_data:
            flash('Failed to generate tailored resume. Please try again.', 'danger')
            return redirect(url_for('user.jobs'))

        # Generate the new PDF
        filename = f"Tailored_Resume_{job.id}_{int(time.time())}.pdf"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        generate_resume_pdf_from_profile(tailored_data, save_path)
        
        return send_file(
            save_path, 
            as_attachment=True, 
            download_name=f"Resume_for_{job.title.replace(' ', '_')}.pdf"
        )

    except Exception as e:
        current_app.logger.error(f"Tailoring Error: {e}")
        flash('An error occurred while tailoring your resume.', 'danger')
        return redirect(url_for('user.jobs'))

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm()
    password_form = ChangePasswordForm()

    if 'update_profile' in request.form and profile_form.validate_on_submit():
        # Check if username/email taken by others
        existing_user = User.query.filter((User.username == profile_form.username.data) | (User.email == profile_form.email.data)).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username or Email already taken.', 'danger')
        else:
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))

    if 'change_password' in request.form and password_form.validate_on_submit():
        if not current_user.check_password(password_form.old_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully.', 'success')
        return redirect(url_for('user.profile'))

    # Pre-populate profile form
    if request.method == 'GET':
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email

    return render_template('user/profile.html', profile_form=profile_form, password_form=password_form)

@user.route('/dashboard')

@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    
    # Pagination for analyses (5 per page)
    analyses_pagination = UserData.query.filter_by(user_id=current_user.id)\
        .order_by(UserData.uploaded_at.desc())\
        .paginate(page=page, per_page=5, error_out=False)
    
    analyses = analyses_pagination.items

    applications = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.applied_at.desc()).all()
    tests = MockTest.query.filter_by(user_id=current_user.id).order_by(MockTest.taken_at.desc()).all()
    interviews = MockInterview.query.filter_by(user_id=current_user.id).order_by(MockInterview.started_at.desc()).all()
    
    resume_form = ResumeBuilderForm()
    linkedin_form = LinkedInBuilderForm()
    
    # Prepare data for Progress Chart (Get all for trend, independent of pagination)
    all_analyses = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.asc()).all()
    resume_scores = []
    for a in all_analyses:
        score = a.analysis_result.get('resume_score')
        if score:
            try:
                resume_scores.append({
                    'timestamp': a.uploaded_at.strftime('%Y-%m-%d %H:%M'),
                    'score': int(score)
                })
            except:
                pass
    
    # Gamification Data
    xp_profile = UserXP.query.filter_by(user_id=current_user.id).first()
    if not xp_profile:
        xp_profile = UserXP(user_id=current_user.id, total_xp=0, level=1)
        db.session.add(xp_profile)
        db.session.commit()
    
    # Auto-assign the first quest if none active
    active_quests = UserQuest.query.filter_by(user_id=current_user.id).all()
    if not active_quests:
        first_quest = Quest.query.first()
        if first_quest:
            uq = UserQuest(user_id=current_user.id, quest_id=first_quest.id, status='in_progress', progress={'count': 0})
            db.session.add(uq)
            db.session.commit()
            
    active_quests = UserQuest.query.filter_by(user_id=current_user.id, status='in_progress').all()
    completed_quests = UserQuest.query.filter_by(user_id=current_user.id, status='completed').all()

    return render_template('user/dashboard.html', 
                           analyses=analyses, 
                           analyses_pagination=analyses_pagination,
                           applications=applications, 
                           tests=tests, 
                           interviews=interviews,
                           resume_form=resume_form,
                           linkedin_form=linkedin_form,
                           resume_scores=resume_scores,
                           xp_profile=xp_profile,
                           active_quests=active_quests,
                           completed_quests=completed_quests)

# --- Resume Analysis ---


@user.route('/resume_analysis', methods=['GET', 'POST'])
@login_required
def resume_analysis():
    print(f"DEBUG: Entering resume_analysis route. Method: {request.method}", flush=True)
    form = ResumeAnalysisForm()
    if request.method == 'POST':
        print("DEBUG: Resume analysis request received!", flush=True)
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided.'}), 400

        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'error': 'No selected file.'}), 400

        job_description = request.form.get('job_description', '')

        try:
            filename = secure_filename(
                f"{current_user.id}_{resume_file.filename}")
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            resume_path = os.path.join(upload_folder, filename)
            resume_file.save(resume_path)
            print(f"DEBUG: File saved to {resume_path}", flush=True)

            resume_text = extract_text_from_pdf(resume_path)
            page_count = get_pdf_page_count(resume_path)
            analysis_result = analyze_resume(resume_text, job_description)

            if not analysis_result:
                return jsonify({'error': 'Could not analyze the resume.'}), 500

            analysis_result['page_count'] = page_count

            user_data = UserData(user_id=current_user.id,
                                 resume_path=filename,
                                 analysis_result=analysis_result)
            db.session.add(user_data)
            db.session.commit()

            # Index for Employer Search
            try:
                skills = analysis_result.get('actual_skills', [])
                add_resume_to_vector_db(current_user.id, resume_text, skills)
            except Exception as e:
                current_app.logger.error(f"Vector Indexing Error: {e}")

            # Gamification
            award_xp(current_user, 50, "Resume Analysis")
            check_quest_progress(current_user, "resume_analysis")

            redirect_url = url_for(
                'user.resume_analysis_result', user_data_id=user_data.id)
            return jsonify({'redirect_url': redirect_url})

        except Exception as e:
            return jsonify({'error': 'An internal error occurred during analysis.'}), 500

    return render_template('user/resume_analysis.html', form=form)


@user.route('/resume_analysis_result/<int:user_data_id>')
@login_required
def resume_analysis_result(user_data_id):
    user_data = UserData.query.get_or_404(user_data_id)
    # Ensure user owns this data
    if user_data.user_id != current_user.id:
        abort(403)
        
    predicted_field = user_data.analysis_result.get('predicted_field', '')
    from ..utils.resource_utils import get_curated_courses, get_dynamic_bonus_videos
    curated_courses = get_curated_courses(predicted_field)
    bonus_videos = get_dynamic_bonus_videos(user_data.analysis_result)
    
    return render_template('user/resume_analysis_result.html', 
                           result=user_data.analysis_result, 
                           user_data_id=user_data.id, 
                           user_data=user_data,
                           curated_courses=curated_courses,
                           bonus_videos=bonus_videos)


@user.route('/download_report/<int:user_data_id>/<format>')
@login_required
def download_report(user_data_id, format):
    user_data = UserData.query.get_or_404(user_data_id)
    if user_data.user_id != current_user.id:
        abort(403)

    result = user_data.analysis_result
    report_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], f"report_{user_data.id}.{format}")

    if format == 'pdf':
        generate_pdf_report(result, report_path)
        return send_file(report_path, as_attachment=True)
    elif format == 'docx':
        generate_docx_report(result, report_path)
        return send_file(report_path, as_attachment=True)
    elif format == 'json':
        import json
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=4)
        return send_file(report_path, as_attachment=True)

    return redirect(url_for('user.resume_analysis_result', user_data_id=user_data.id))

# --- Conversational Assessment ---


@user.route('/start_assessment/<int:user_data_id>')
@login_required
def start_assessment(user_data_id):
    user_data = UserData.query.get_or_404(user_data_id)
    if user_data.user_id != current_user.id:
        abort(403)

    session['assessment_history'] = []
    session['current_user_data_id'] = user_data_id

    question_data = generate_next_assessment_question([], user_data.analysis_result.get(
        'predicted_field'), user_data.analysis_result.get('experience_level'))

    if question_data.get('status') == 'completed':
        flash('Assessment already completed or unavailable.')
        return redirect(url_for('user.resume_analysis_result', user_data_id=user_data_id))

    return render_template('user/assessment.html', question=question_data, user_data_id=user_data_id)


@user.route('/submit_assessment_answer', methods=['POST'])
@login_required
def submit_assessment_answer():
    answer = request.form.get('answer')
    question = request.form.get('question')
    user_data_id = session.get('current_user_data_id')

    if not user_data_id:
        return redirect(url_for('user.dashboard'))

    user_data = UserData.query.get_or_404(user_data_id)
    history = session.get('assessment_history', [])
    history.append({'question': question, 'answer': answer})
    session['assessment_history'] = history

    question_data = generate_next_assessment_question(history, user_data.analysis_result.get(
        'predicted_field'), user_data.analysis_result.get('experience_level'))

    if question_data.get('status') == 'completed':
        # Update analysis
        updated_analysis = generate_updated_analysis(
            user_data.analysis_result, history)
        user_data.analysis_result = updated_analysis
        db.session.commit()
        flash('Assessment completed! Your analysis has been updated.')
        return redirect(url_for('user.resume_analysis_result', user_data_id=user_data_id))

    return render_template('user/assessment.html', question=question_data, user_data_id=user_data_id)

# --- Resume Builder ---


@user.route('/resume_builder', methods=['GET', 'POST'])
@login_required
def resume_builder():
    form = ResumeBuilderForm()
    if form.validate_on_submit():
        data = {
            'full_name': form.full_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'linkedin': form.linkedin.data,
            'summary': form.summary.data,
            'education_school': form.education_school.data,
            'education_degree': form.education_degree.data,
            'education_year': form.education_year.data,
            'job_title': form.job_title.data,
            'company': form.company.data,
            'job_description': form.job_description.data,
            'skills': form.skills.data
        }

        filename = f"resume_{current_user.id}_generated.pdf"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        generate_resume_pdf(data, save_path)

        return send_file(save_path, as_attachment=True)

    return render_template('user/resume_builder.html', form=form)

# --- LinkedIn Builder ---


@user.route('/linkedin_builder', methods=['GET', 'POST'])
@login_required
def linkedin_builder():
    form = LinkedInBuilderForm()
    if form.validate_on_submit():
        content = generate_linkedin_content(
            form.current_role.data, form.skills.data, form.achievements.data)

        filename = f"linkedin_profile_{current_user.id}.txt"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(f"Headline:\n{content.get('headline', '')}\n\n")
            f.write(f"About:\n{content.get('about', '')}\n\n")
            f.write("Experience Bullets:\n")
            for bullet in content.get('experience_bullets', []):
                f.write(f"- {bullet}\n")

        return render_template('user/linkedin_result.html', content=content, filename=filename)

    return render_template('user/linkedin_builder.html', form=form)


@user.route('/download_linkedin/<filename>')
@login_required
def download_linkedin(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# --- New LinkedIn Optimizer (Full Profile) ---

@user.route('/linkedin_optimizer')
@login_required
def linkedin_optimizer():
    return render_template('user/linkedin_optimizer.html')

@user.route('/api/optimize_linkedin', methods=['POST'])
@login_required
def api_optimize_linkedin():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Process using AI
    result = optimize_linkedin_profile(data)
    return jsonify(result)

@user.route('/download_optimized_linkedin', methods=['POST'])
@login_required
def download_optimized_linkedin():
    try:
        raw_data = request.form.get('data')
        if not raw_data:
            flash('No data to download.', 'danger')
            return redirect(url_for('user.linkedin_optimizer'))
            
        profile = json.loads(raw_data)
        
        # Build Text Content
        lines = []
        lines.append(f"LINKEDIN PROFILE OPTIMIZATION FOR {current_user.username.upper()}")
        lines.append("="*50)
        lines.append("")
        
        lines.append("--- HEADLINE ---")
        lines.append(profile.get('headline', ''))
        lines.append("")
        
        lines.append("--- ABOUT ---")
        lines.append(profile.get('about', ''))
        lines.append("")
        
        lines.append("--- EXPERIENCE ---")
        for job in profile.get('experience', []):
            lines.append(f"{job.get('title')} | {job.get('company')}")
            lines.append(f"{job.get('dates')} | {job.get('location')}")
            lines.append(job.get('description', ''))
            lines.append("-" * 20)
        lines.append("")
        
        lines.append("--- EDUCATION ---")
        for edu in profile.get('education', []):
            lines.append(f"{edu.get('school')} - {edu.get('degree')}")
            lines.append(f"{edu.get('dates')}")
            lines.append("")
            
        lines.append("--- SKILLS ---")
        lines.append(profile.get('skills', ''))
        lines.append("")
        
        lines.append("--- PROJECTS ---")
        for proj in profile.get('projects', []):
            lines.append(f"{proj.get('name')}")
            lines.append(f"{proj.get('description')}")
            lines.append("")
            
        content = "\n".join(lines)
        
        # Create a BytesIO object
        mem = io.BytesIO()
        mem.write(content.encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            as_attachment=True,
            download_name=f"Optimized_LinkedIn_Profile_{current_user.username}.txt",
            mimetype='text/plain'
        )
    except Exception as e:
        current_app.logger.error(f"Download Error: {e}")
        flash('Error generating download file.', 'danger')
        return redirect(url_for('user.linkedin_optimizer'))

@user.route('/download_resume_pdf_optimized', methods=['POST'])
@login_required
def download_resume_pdf_optimized():
    try:
        raw_data = request.form.get('data')
        if not raw_data:
            flash('No data to download.', 'danger')
            return redirect(url_for('user.linkedin_optimizer'))
            
        profile = json.loads(raw_data)
        
        # Ensure we have a temp file path
        filename = f"Optimized_Resume_{current_user.id}_{int(time.time())}.pdf"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        generate_resume_pdf_from_profile(profile, save_path)
        
        return send_file(save_path, as_attachment=True, download_name=f"Optimized_Resume_{current_user.username}.pdf")
        
    except Exception as e:
        current_app.logger.error(f"PDF Download Error: {e}")
        flash('Error generating PDF.', 'danger')
        return redirect(url_for('user.linkedin_optimizer'))


# --- Job Applications ---


@user.route('/jobs')
@login_required
def jobs():
    # Fetch all jobs sorted by date
    all_jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    applied_job_ids = [app.job_id for app in current_user.applications]
    
    recommended_jobs = []
    
    # Get user's latest resume text for match calculation
    latest_resume = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
    
    resume_text = ""
    if latest_resume:
        try:
            resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_resume.resume_path)
            resume_text = extract_text_from_pdf(resume_path)
            
            # Vector Search for Recommendations
            recommended_ids = search_jobs_by_resume(resume_text, n_results=3)
            if recommended_ids:
                recommended_jobs = [j for j in all_jobs if j.id in recommended_ids]
                
        except Exception as e:
            current_app.logger.error(f"Vector search failed: {e}")
            pass

    return render_template('user/jobs.html', jobs=all_jobs, recommended_jobs=recommended_jobs, applied_job_ids=applied_job_ids, has_resume=bool(latest_resume))

@user.route('/application_details/<int:app_id>')
@login_required
def application_details(app_id):
    application = JobApplication.query.get_or_404(app_id)
    if application.user_id != current_user.id:
        abort(403)
    return render_template('user/application_details.html', application=application)

@user.route('/api/calculate_match', methods=['POST'])
@login_required
def calculate_match():
    data = request.get_json()
    job_id = data.get('job_id')
    job = JobPosting.query.get_or_404(job_id)
    
    latest_resume = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
    if not latest_resume:
        return jsonify({'error': 'No resume found'}), 400
        
    try:
        resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_resume.resume_path)
        resume_text = extract_text_from_pdf(resume_path)
        
        # Simple AI prompt for match score
        from ..utils.ai_utils import _call_gemini
        prompt = f"""Rate the match between this resume and job description from 0 to 100.
        Return ONLY a JSON object: {{"score": 85, "reason": "short explanation"}}
        
        Resume: {resume_text[:2000]}
        Job: {job.description[:1000]}"""
        
        result = _call_gemini(prompt, response_mime_type='application/json')
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@user.route('/api/generate_cover_letter', methods=['POST'])
@login_required
def api_generate_cover_letter():
    data = request.get_json()
    job_id = data.get('job_id')
    
    if not job_id:
        return jsonify({'error': 'Job ID is required'}), 400
        
    job = JobPosting.query.get_or_404(job_id)
    
    # Get latest resume
    latest_resume = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
    
    if not latest_resume:
        return jsonify({'error': 'Please upload a resume first.'}), 400
        
    try:
        resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_resume.resume_path)
        resume_text = extract_text_from_pdf(resume_path)
        
        result = generate_cover_letter(resume_text, job.description)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user.route('/apply/<int:job_id>')
@login_required
def apply(job_id):
    job = JobPosting.query.get_or_404(job_id)

    if JobApplication.query.filter_by(user_id=current_user.id, job_id=job.id).first():
        flash('You have already applied for this job.')
        return redirect(url_for('user.jobs'))

    user_data = UserData.query.filter_by(user_id=current_user.id).order_by(
        UserData.uploaded_at.desc()).first()
    if not user_data:
        flash('Please upload a resume before applying for a job.')
        return redirect(url_for('user.resume_analysis'))

    application = JobApplication(user_id=current_user.id,
                                 job_id=job.id,
                                 resume_path=user_data.resume_path)
    db.session.add(application)

    notification = Notification(user_id=job.created_by,
                                message=f'{current_user.username} has applied for your job posting: {job.title}')
    db.session.add(notification)
    db.session.commit()

    # Gamification
    award_xp(current_user, 20, f"applying for {job.title}")
    check_quest_progress(current_user, "job_apply")

    flash('You have successfully applied for the job.')
    return redirect(url_for('user.jobs'))

# --- Interview Prep ---


@user.route('/interview_prep')
@login_required
def interview_prep():
    return render_template('user/interview_prep.html')

# --- Mock Interview ---


@user.route('/mock_interview')
@login_required
def mock_interview():
    # Using the new Real-Time AI Coach interface
    return render_template('user/interview_mode.html')


@socketio.on('start_interview')
def handle_start_interview(data):
    # Fetch user's latest resume analysis for context
    if current_user.is_authenticated:
        user_data = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
        if user_data and user_data.analysis_result:
            context = {
                'field': user_data.analysis_result.get('predicted_field', 'General'),
                'level': user_data.analysis_result.get('experience_level', 'N/A'),
                'skills': user_data.analysis_result.get('actual_skills', []),
                'summary': user_data.analysis_result.get('ai_summary', '')[:500] # Truncate for token limit
            }
            session['interview_context'] = json.dumps(context)
        else:
            session['interview_context'] = None
            
    question = get_interview_question("Tell me about yourself.", "start")
    emit('interview_question', {'question': question})


@socketio.on('send_answer')
def handle_send_answer(data):
    answer = data['answer']
    # Retrieve context from session
    context_json = session.get('interview_context')
    context = json.loads(context_json) if context_json else None
    
    question = get_interview_question(answer, "continue", resume_context=context)
    emit('interview_question', {'question': question})

@user.route('/skill_tree')
@login_required
def skill_tree():
    # Fetch user XP and quest data for the Skill Tree
    xp_profile = UserXP.query.filter_by(user_id=current_user.id).first()
    if not xp_profile:
        from ..services.gamification_service import gamification_service
        gamification_service.initialize_user_xp(current_user.id)
        xp_profile = UserXP.query.filter_by(user_id=current_user.id).first()
        
    return render_template('user/skill_tree.html', xp_profile=xp_profile)

# --- Mock Test ---


@user.route('/mock_test', methods=['GET', 'POST'])
@login_required
def mock_test():
    form = MockTestForm()
    if form.validate_on_submit():
        topic = form.topic.data
        test_data = generate_mock_test(topic)
        if test_data:
            mock_test = MockTest(user_id=current_user.id,
                                 questions=test_data)
            db.session.add(mock_test)
            db.session.commit()
            return render_template('user/mock_test_start.html', test=mock_test, topic=topic)
        else:
            flash('Could not generate a test for the given topic.')
    return render_template('user/mock_test.html', form=form)


@user.route('/submit_test/<int:test_id>', methods=['POST'])
@login_required
def submit_test(test_id):
    test = MockTest.query.get_or_404(test_id)
    score = 0
    for i, q in enumerate(test.questions['questions']):
        selected_answer = request.form.get(f'question-{i}')
        if selected_answer == q['correct_answer']:
            score += 1

    test.score = (score / len(test.questions['questions'])) * 100
    db.session.commit()

    # Gamification
    award_xp(current_user, 100, "completing a Mock Test")
    check_quest_progress(current_user, "mock_test")

    flash(f'You scored {test.score}% on the test.')
    return redirect(url_for('user.dashboard'))


# --- AI Assistant APIs ---

@user.route('/api/generate_summary', methods=['POST'])
@login_required
def api_generate_summary():
    data = request.get_json()
    job_title = data.get('job_title')
    skills = data.get('skills')
    
    if not job_title:
        return jsonify({'error': 'Job title is required'}), 400
        
    result = generate_professional_summary(job_title, skills or "General")
    if result:
        return jsonify(result)
    return jsonify({'error': 'Failed to generate summary'}), 500


@user.route('/api/refine_experience', methods=['POST'])
@login_required
def api_refine_experience():
    data = request.get_json()
    role = data.get('role')
    raw_text = data.get('raw_text')
    
    if not role or not raw_text:
        return jsonify({'error': 'Role and raw text are required'}), 400
        
    result = refine_experience_points(role, raw_text)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Failed to refine experience'}), 500


@user.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    file_owner_id_str = filename.split('_')[0]
    if not file_owner_id_str.isdigit():
        abort(404)
    file_owner_id = int(file_owner_id_str)

    if current_user.role != 'admin' and current_user.id != file_owner_id:
        abort(403)

    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

# --- Custom AI Agent ---
from ..utils.agent import CareerAgent
from ..services.career_forecast_service import CareerForecastService

@user.route('/future_career', methods=['GET', 'POST'])
@login_required
def future_career():
    forecast_service = CareerForecastService(current_user.id)
    latest_forecast = forecast_service.get_latest_forecast()
    
    if request.method == 'POST':
        target_role = request.form.get('target_role')
        if not target_role:
            flash('Please enter a target role.', 'danger')
            return redirect(url_for('user.future_career'))
            
        try:
            result = forecast_service.generate_forecast(target_role)
            if 'error' in result:
                flash(result['error'], 'danger')
            else:
                flash('Career forecast generated successfully!', 'success')
                return redirect(url_for('user.future_career'))
                
        except Exception as e:
            current_app.logger.error(f"Forecast Error: {e}")
            flash('An error occurred while generating the forecast.', 'danger')
            return redirect(url_for('user.future_career'))

    return render_template('user/future_dashboard.html', forecast=latest_forecast)

@user.route('/ats_simulator')
@login_required
def ats_simulator():
    latest_resume = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).first()
    if not latest_resume:
        flash('Please upload a resume first to use the ATS Simulator.', 'warning')
        return redirect(url_for('user.resume_analysis'))
        
    try:
        resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_resume.resume_path)
        resume_text = extract_text_from_pdf(resume_path)
        
        analysis = simulate_ats_parsing(resume_text)
        if not analysis:
            flash('Failed to simulate ATS parsing. Please try again.', 'danger')
            return redirect(url_for('user.dashboard'))
            
        return render_template('user/ats_simulator.html', analysis=analysis)
    except Exception as e:
        current_app.logger.error(f"ATS Simulator Error: {e}")
        flash('An error occurred during ATS simulation.', 'danger')
        return redirect(url_for('user.dashboard'))

@user.route('/co_writer')
@login_required
def co_writer():
    return render_template('user/co_writer.html')

@user.route('/api/co_writer_suggest', methods=['POST'])
@login_required
def api_co_writer_suggest():
    data = request.get_json()
    content = data.get('content', '')
    context = data.get('context', 'Professional Resume') # e.g., "Experience Section"
    
    if not content:
        return jsonify({'suggestions': []})
        
    prompt = f"""
    You are an expert Resume AI Co-Writer. 
    The user is currently writing this section: "{context}".
    
    Current Text:
    "{content}"
    
    Task:
    Provide 3 professional, high-impact completions or improvements for the current text.
    Focus on using strong action verbs, quantifiable metrics, and industry keywords.
    
    Return a JSON object:
    {{
        "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
    }}
    """
    
    result = _call_gemini(prompt, response_mime_type='application/json')
    return jsonify(result or {'suggestions': []})

@user.route('/agent_chat')
@login_required
def agent_chat():
    return render_template('user/agent_chat.html')

@user.route('/api/agent_chat', methods=['POST'])
@login_required
def api_agent_chat():
    data = request.get_json()
    user_message = data.get('message')
    # Local agent doesn't strictly need history, but we could pass it if we wanted context.
    
    agent = CareerAgent(current_user)
    response_text = agent.chat(user_message)
    
    return jsonify({'response': response_text})
