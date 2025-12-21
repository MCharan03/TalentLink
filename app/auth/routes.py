from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, Notification
from .forms import LoginForm, RegistrationForm
from ..extensions import db
from ..utils.email_utils import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                if user.role == 'admin':
                    next = url_for('admin.dashboard')
                else:
                    next = url_for('user.dashboard')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Create a notification for the new user
        notification = Notification(
            user_id=user.id, message="Welcome to the Smart Resume Analyzer!")
        db.session.add(notification)
        db.session.commit()

        # Send welcome email
        try:
            send_email(
                to=user.email,
                subject="Welcome to Smart Resume Analyzer",
                template=None,
                body=f"Hello {user.username},\n\nWelcome to Smart Resume Analyzer! We are excited to have you on board.\n\nStart analyzing your resume today!"
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
