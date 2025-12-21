import os
from flask import render_template, redirect, url_for, flash, request, send_file, current_app, jsonify, send_from_directory, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import user
from .forms import ResumeAnalysisForm, MockTestForm, ResumeBuilderForm, LinkedInBuilderForm
from ..extensions import db, socketio
from ..models import UserData, MockTest, JobPosting, JobApplication, Notification, MockInterview
from ..utils.file_utils import extract_text_from_pdf, get_pdf_page_count
from ..utils.ai_utils import analyze_resume, get_interview_question, generate_mock_test, generate_linkedin_content, generate_next_assessment_question, generate_updated_analysis
from ..utils.report_utils import generate_pdf_report, generate_docx_report, generate_resume_pdf


@user.route('/dashboard')


@login_required


def dashboard():


    analyses = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.uploaded_at.desc()).all()


    applications = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.applied_at.desc()).all()


    tests = MockTest.query.filter_by(user_id=current_user.id).order_by(MockTest.taken_at.desc()).all()


    interviews = MockInterview.query.filter_by(user_id=current_user.id).order_by(MockInterview.started_at.desc()).all()


    


    resume_form = ResumeBuilderForm()


    linkedin_form = LinkedInBuilderForm()


    


    # Prepare data for Progress Chart


    resume_scores = []


    for a in analyses:


        score = a.analysis_result.get('resume_score')


        if score:


            try:


                resume_scores.append({


                    'timestamp': a.uploaded_at.strftime('%Y-%m-%d %H:%M'),


                    'score': int(score)


                })


            except:


                pass


    resume_scores.reverse() # Oldest first for line chart


    


    return render_template('user/dashboard.html', 


                           analyses=analyses, 


                           applications=applications, 


                           tests=tests, 


                           interviews=interviews,


                           resume_form=resume_form,


                           linkedin_form=linkedin_form,


                           resume_scores=resume_scores)

# --- Resume Analysis ---


@user.route('/resume_analysis', methods=['GET', 'POST'])
@login_required
def resume_analysis():
    form = ResumeAnalysisForm()
    if request.method == 'POST':
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
    return render_template('user/resume_analysis_result.html', result=user_data.analysis_result, user_data_id=user_data.id, user_data=user_data)


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

# --- Job Applications ---


@user.route('/jobs')
@login_required
def jobs():
    jobs = JobPosting.query.all()
    return render_template('user/jobs.html', jobs=jobs)


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
    return render_template('user/mock_interview_session.html')


@socketio.on('start_interview')
def handle_start_interview(data):
    question = get_interview_question("Tell me about yourself.", "start")
    emit('interview_question', {'question': question})


@socketio.on('send_answer')
def handle_send_answer(data):
    answer = data['answer']
    question = get_interview_question(answer, "continue")
    emit('interview_question', {'question': question})

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

    flash(f'You scored {test.score}% on the test.')
    return redirect(url_for('user.dashboard'))


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
