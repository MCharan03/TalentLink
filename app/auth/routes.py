from flask import render_template, redirect, request, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, Notification
from .forms import LoginForm, RegistrationForm
from ..extensions import db, oauth
from ..utils.email_utils import send_email
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
        social_id = user_info.get('sub') # LinkedIn OpenID uses 'sub'
        
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
            
        login_user(user)
        # Handle role-based redirect
        next_url = url_for('admin.dashboard') if user.role == 'admin' else url_for('user.dashboard')
        return redirect(next_url)
    
    else:
        # New User - Create Account
        # Ensure username is unique
        base_username = name.replace(' ', '').lower() if name else email.split('@')[0]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        new_user = User(email=email, username=username, role='user')
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


from ..models import User, Notification, Company, EmployerProfile
from .forms import LoginForm, RegistrationForm, EmployerRegistrationForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            # Check for employer approval
            if user.role == 'employer':
                if not user.employer_profile or not user.employer_profile.is_verified:
                    flash('Your account is pending approval. Please check your email for status updates.', 'warning')
                    return render_template('auth/login.html', form=form)

            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                if user.role == 'admin':
                    next = url_for('admin.dashboard')
                elif user.role == 'employer':
                    next = url_for('employer.dashboard')
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
    # Candidate Registration
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    role='user')
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

        # Send welcome email (Welcome Persona)
        try:
            send_email(
                to=user.email,
                subject="Welcome to Smart Resume Analyzer",
                template=None,
                category='general',
                body=f"Hello {user.username},\n\nWelcome to Smart Resume Analyzer! We are excited to have you on board.\n\nStart analyzing your resume today!"
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    form = EmployerRegistrationForm()
    if form.validate_on_submit():
        # 1. Create User (No password yet, or random unusable one)
        # We set a placeholder password that cannot be used until admin resets it
        import secrets
        temp_pass = secrets.token_urlsafe(16)
        
        user = User(email=form.email.data,
                    username=form.username.data,
                    role='employer')
        user.set_password(temp_pass)
        db.session.add(user)
        db.session.flush() # Get ID

        # 2. Create Company & Profile
        company = Company.query.filter_by(name=form.company_name.data).first()
        if not company:
            company = Company(name=form.company_name.data)
            db.session.add(company)
            db.session.flush()
            
        profile = EmployerProfile(user_id=user.id, company_id=company.id, is_verified=False)
        db.session.add(profile)
        db.session.commit()

        # 3. Send Email to Applicant
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

        # 4. Notify Admin (Optional: Email or DB Notification)
        # For now, we assume admin checks dashboard or gets a notification if we had an admin user to target
        
        flash('Request submitted successfully! We will notify you via email upon approval.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/employer_register.html', form=form)


