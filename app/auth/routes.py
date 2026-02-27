from flask import render_template, redirect, request, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, Notification, Company, EmployerProfile
from .forms import LoginForm, RegistrationForm, EmployerRegistrationForm, ForgotPasswordForm, ResetPasswordForm
from ..extensions import db, oauth
from ..utils.email_utils import send_email
from ..utils.auth_utils import (
    generate_verification_token, confirm_verification_token,
    generate_reset_token, confirm_reset_token,
    check_rate_limit, record_failed_attempt, clear_login_attempts
)
from datetime import datetime
import os

# --- OAuth Configuration ---
def get_google_client():
    return oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid email profile'},
    )

def get_linkedin_client():
    return oauth.register(
        name='linkedin',
        client_id=os.getenv('LINKEDIN_CLIENT_ID'),
        client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
        access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
        access_token_params=None,
        authorize_url='https://www.linkedin.com/oauth/v2/authorization',
        authorize_params=None,
        api_base_url='https://api.linkedin.com/v2/',
        client_kwargs={'scope': 'openid profile email'},
    )


@auth.route('/oauth/<provider>')
def oauth_login(provider):
    if provider == 'google':
        client = get_google_client()
        redirect_uri = url_for('auth.oauth_authorize', provider='google', _external=True)
        return client.authorize_redirect(redirect_uri)
    elif provider == 'linkedin':
        client = get_linkedin_client()
        redirect_uri = url_for('auth.oauth_authorize', provider='linkedin', _external=True)
        return client.authorize_redirect(redirect_uri)
    else:
        flash('Unsupported login provider.', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/authorize/<provider>')
def oauth_authorize(provider):
    if provider == 'google':
        client = get_google_client()
        token = client.authorize_access_token()
        user_info = client.get('userinfo').json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        social_id = user_info.get('id')
        
    elif provider == 'linkedin':
        client = get_linkedin_client()
        token = client.authorize_access_token()
        user_info = client.get('userinfo').json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        social_id = user_info.get('sub')  # LinkedIn OpenID uses 'sub'
        
    else:
        flash('Unknown provider', 'danger')
        return redirect(url_for('auth.login'))

    # Common Login Logic
    if not email:
        flash('Could not retrieve email from social login.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if user:
        # User exists, link account if not linked
        if provider == 'google' and not user.google_id:
            user.google_id = social_id
            db.session.commit()
        elif provider == 'linkedin' and not user.linkedin_id:
            user.linkedin_id = social_id
            db.session.commit()
        
        # OAuth users are auto-verified
        if not user.is_verified:
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            db.session.commit()
            
        login_user(user)
        next_url = url_for('admin.dashboard') if user.role == 'admin' else url_for('user.dashboard')
        return redirect(next_url)
    
    else:
        # New User - Create Account
        base_username = name.replace(' ', '').lower() if name else email.split('@')[0]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        new_user = User(email=email, username=username, role='user',
                        is_verified=True, verified_at=datetime.utcnow())
        if provider == 'google':
            new_user.google_id = social_id
        elif provider == 'linkedin':
            new_user.linkedin_id = social_id
            
        db.session.add(new_user)
        db.session.commit()
        
        # Initialize Gamification Profile
        from ..services.gamification_service import gamification_service
        gamification_service.initialize_user_xp(new_user.id)
        
        # Welcome items
        notification = Notification(user_id=new_user.id, message="Welcome! You've successfully signed up via " + provider.capitalize())
        db.session.add(notification)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('user.dashboard'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data

        # Rate limiting check
        is_locked, remaining = check_rate_limit(email)
        if is_locked:
            minutes = remaining // 60
            flash(f'Too many failed attempts. Account locked for {minutes} more minute(s). Please try again later.', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(form.password.data):
            # Check email verification (skip for admin, employer, and OAuth users)
            if not user.is_verified and user.role not in ('admin', 'employer') and not user.google_id and not user.linkedin_id:
                flash('Please verify your email before logging in. Check your inbox for the verification link.', 'warning')
                return render_template('auth/login.html', form=form)

            # Check for employer approval
            if user.role == 'employer':
                if not user.employer_profile or not user.employer_profile.is_verified:
                    flash('Your account is pending approval. Please check your email for status updates.', 'warning')
                    return render_template('auth/login.html', form=form)

            clear_login_attempts(email)
            login_user(user, form.remember_me.data)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                if user.role == 'admin':
                    next_page = url_for('admin.dashboard')
                elif user.role == 'employer':
                    next_page = url_for('employer.dashboard')
                else:
                    next_page = url_for('user.dashboard')
            return redirect(next_page)
        
        # Failed login
        record_failed_attempt(email)
        flash('Invalid email or password.', 'danger')
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
                    username=form.username.data,
                    role='user',
                    is_verified=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Initialize Gamification Profile
        from ..services.gamification_service import gamification_service
        gamification_service.initialize_user_xp(user.id)

        # Create a notification for the new user
        notification = Notification(
            user_id=user.id, message="Welcome to the Smart Resume Analyzer!")
        db.session.add(notification)
        db.session.commit()

        # Send verification email
        try:
            token = generate_verification_token(user.email)
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            send_email(
                to=user.email,
                subject="Verify Your Email — Smart Resume Analyzer",
                template=None,
                category='general',
                body=f"Hello {user.username},\n\nWelcome to Smart Resume Analyzer! Please verify your email by clicking the link below:\n\n{verify_url}\n\nThis link expires in 1 hour.\n\nIf you did not sign up, please ignore this email."
            )
            flash('Registration successful! Please check your email to verify your account.', 'success')
        except Exception as e:
            print(f"Error sending verification email: {e}")
            flash('Registration successful! Verification email could not be sent. Please contact support.', 'warning')

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/verify/<token>')
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Email already verified. You can log in.', 'info')
    else:
        user.is_verified = True
        user.verified_at = datetime.utcnow()
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    
    return render_template('auth/verify_email.html')


@auth.route('/resend_verification', methods=['POST'])
def resend_verification():
    email = request.form.get('email')
    if not email:
        flash('Please provide your email address.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        try:
            token = generate_verification_token(user.email)
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            send_email(
                to=user.email,
                subject="Verify Your Email — Smart Resume Analyzer",
                template=None,
                category='general',
                body=f"Hello {user.username},\n\nPlease verify your email by clicking the link below:\n\n{verify_url}\n\nThis link expires in 1 hour."
            )
        except Exception as e:
            print(f"Error resending verification: {e}")
    
    flash('If that email is registered and unverified, a new verification link has been sent.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            try:
                token = generate_reset_token(user.email)
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                send_email(
                    to=user.email,
                    subject="Password Reset — Smart Resume Analyzer",
                    template=None,
                    category='support',
                    body=f"Hello {user.username},\n\nYou requested a password reset. Click the link below to set a new password:\n\n{reset_url}\n\nThis link expires in 30 minutes.\n\nIf you did not request this, please ignore this email."
                )
            except Exception as e:
                print(f"Error sending reset email: {e}")
        
        # Always show success to prevent email enumeration
        flash('If that email is registered, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            clear_login_attempts(email)
            flash('Your password has been reset successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)


@auth.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    form = EmployerRegistrationForm()
    if form.validate_on_submit():
        import secrets
        temp_pass = secrets.token_urlsafe(16)
        
        user = User(email=form.email.data,
                    username=form.username.data,
                    role='employer')
        user.set_password(temp_pass)
        db.session.add(user)
        db.session.flush()

        company = Company.query.filter_by(name=form.company_name.data).first()
        if not company:
            company = Company(name=form.company_name.data)
            db.session.add(company)
            db.session.flush()
            
        profile = EmployerProfile(user_id=user.id, company_id=company.id, is_verified=False)
        db.session.add(profile)
        db.session.commit()

        try:
            send_email(
                to=user.email,
                subject="Employer Request Received - SRA",
                template=None,
                category='general',
                body=f"Hello {user.username},\n\nWe have received your request to join as an Employer/Recruiter for {company.name}.\n\nOur admin team will review your application. Upon approval, you will receive your login credentials via email.\n\nThank you,\nSRA Team"
            )
        except Exception as e:
            print(f"Error sending email: {e}")
        
        flash('Request submitted successfully! We will notify you via email upon approval.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/employer_register.html', form=form)
