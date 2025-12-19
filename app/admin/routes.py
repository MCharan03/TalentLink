from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from . import admin
from .forms import JobPostingForm
from ..extensions import db
from ..models import JobPosting, JobApplication
from ..utils.ai_utils import generate_job_description


@admin.route('/dashboard')
@login_required
def dashboard():
    jobs = JobPosting.query.filter_by(created_by=current_user.id).all()
    return render_template('admin/dashboard.html', jobs=jobs)

@admin.route('/create_job', methods=['GET', 'POST'])
@login_required
def create_job():
    form = JobPostingForm()
    if form.validate_on_submit():
        job = JobPosting(title=form.title.data,
                         description=form.description.data,
                         created_by=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('The job posting has been created.')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_job.html', form=form)

@admin.route('/generate_jd', methods=['POST'])
@login_required
def generate_jd():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Job title is required'}), 400
    
    description = generate_job_description(title)
    return jsonify({'description': description})

@admin.route('/applicant/<int:application_id>')
@login_required
def applicant_details(application_id):
    application = JobApplication.query.get_or_404(application_id)
    return render_template('admin/applicant_details.html', application=application)
