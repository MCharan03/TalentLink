from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import current_user
import io
import csv
from datetime import datetime

from . import admin
from .forms import JobPostingForm
from ..extensions import db
from ..models import JobPosting, JobApplication, User, UserData, MockTest, MockInterview, Notification
from ..utils.ai_utils import generate_job_description
from ..decorators import admin_required


@admin.route('/dashboard')
@admin_required
def dashboard():
    # Fetch user data for the table
    user_data = UserData.query.order_by(UserData.uploaded_at.desc()).all()
    
    # Simple analytics
    from sqlalchemy import func
    analysis_dates = db.session.query(func.date(UserData.uploaded_at), func.count(UserData.id)).group_by(func.date(UserData.uploaded_at)).all()
    
    engagement_dates = [d[0].strftime('%Y-%m-%d') for d in analysis_dates]
    analysis_counts = [d[1] for d in analysis_dates]

    return render_template('admin/dashboard.html', 
                           user_data=user_data,
                           engagement_dates=engagement_dates,
                           analysis_counts=analysis_counts)

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
        flash('Job posting created.', 'success')
    return redirect(url_for('admin.interview_funnel'))