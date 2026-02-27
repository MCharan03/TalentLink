from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    linkedin_id = db.Column(db.String(100), unique=True, nullable=True)
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    xp_profile = db.relationship('UserXP', backref='user', uselist=False, cascade='all, delete-orphan')
    github_profile = db.relationship('GitHubProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class UserData(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resume_path = db.Column(db.String(255))
    analysis_result = db.Column(db.JSON)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref(
        'user_data', lazy=True, cascade='all, delete-orphan'))


class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.relationship(
        'User', backref=db.backref('job_postings', lazy=True))


class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'))
    resume_path = db.Column(db.String(255))
    # e.g., submitted, under review, rejected, accepted
    status = db.Column(db.String(20), default='submitted')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref(
        'applications', lazy=True, cascade='all, delete-orphan'))
    job = db.relationship(
        'JobPosting', backref=db.backref('applications', lazy=True, cascade='all, delete-orphan'))


class ExternalApplication(db.Model):
    __tablename__ = 'external_applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_name = db.Column(db.String(255))
    job_title = db.Column(db.String(255))
    job_url = db.Column(db.String(500))
    job_description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Wishlist') # Wishlist, Applied, Interviewing, Offer, Rejected
    match_score = db.Column(db.Integer)
    match_summary = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('external_applications', lazy=True, cascade='all, delete-orphan'))


class MockTest(db.Model):
    __tablename__ = 'mock_tests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    questions = db.Column(db.JSON)
    score = db.Column(db.Float)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref(
        'mock_tests', lazy=True, cascade='all, delete-orphan'))


class MockInterview(db.Model):
    __tablename__ = 'mock_interviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    interview_type = db.Column(db.String(20), default='mixed')  # behavioral, technical, mixed
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    transcript = db.Column(db.Text)
    feedback = db.Column(db.Text)
    score = db.Column(db.Integer)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref(
        'mock_interviews', lazy=True, cascade='all, delete-orphan'))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref(
        'notifications', lazy='dynamic', cascade='all, delete-orphan'))


# --- Gamification & Advanced Features ---

class UserXP(db.Model):
    __tablename__ = 'user_xp'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    energy = db.Column(db.Integer, default=100)  # User's current energy (0-100)
    achievements = db.Column(db.JSON, default=dict)  # e.g., {"resumes_optimized": 5, "mock_interviews": 2}


class SystemMetric(db.Model):
    __tablename__ = 'system_metrics'
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50))  # 'error', 'request_time', etc.
    route = db.Column(db.String(255))
    value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Quest(db.Model):
    __tablename__ = 'quests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))
    xp_reward = db.Column(db.Integer)
    criteria = db.Column(db.JSON)  # e.g., {"type": "upload_resume", "count": 1}


class UserQuest(db.Model):
    __tablename__ = 'user_quests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
    progress = db.Column(db.JSON, default=dict)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    quest = db.relationship('Quest', backref=db.backref('user_quests', lazy=True))


class GitHubProfile(db.Model):
    __tablename__ = 'github_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    username = db.Column(db.String(100))
    repo_analysis = db.Column(db.JSON)  # Stores AI summary of code quality
    last_scanned = db.Column(db.DateTime, default=datetime.utcnow)


# --- Ecosystem & Future Career Features ---

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employers = db.relationship('EmployerProfile', backref='company', lazy=True)
    jobs = db.relationship('JobPosting', backref='company', lazy=True)


class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    department = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('employer_profile', uselist=False))


class CareerForecast(db.Model):
    """
    Stores the AI-generated 'Future Resume' and career trajectory.
    """
    __tablename__ = 'career_forecasts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target_role = db.Column(db.String(150))
    
    # The JSON structure for the future resume (skills, experience, projects)
    future_resume_json = db.Column(db.JSON) 
    
    # AI analysis of current vs future gaps
    gap_analysis = db.Column(db.JSON)
    
    # A list of milestones/dates (e.g., "Learn Docker by Q3 2026")
    roadmap_timeline = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('career_forecasts', lazy=True, cascade='all, delete-orphan'))


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.String(255))
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_setting(key, default=None):
        setting = SystemSetting.query.filter_by(key=key).first()
        return setting.value if setting else default