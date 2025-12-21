from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Email


class ResumeAnalysisForm(FlaskForm):
    resume = FileField('Upload Resume (PDF)', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDFs only!')
    ])
    job_description = TextAreaField('Job Description (Optional)')
    submit = SubmitField('Analyze')


class MockTestForm(FlaskForm):
    topic = StringField('Enter a topic for the test',
                        validators=[DataRequired()])
    submit = SubmitField('Start Test')


class ResumeBuilderForm(FlaskForm):
    # Personal Info
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    linkedin = StringField('LinkedIn URL')

    # Summary
    summary = TextAreaField('Professional Summary', render_kw={"rows": 4})

    # Education (Simplified: Single block for MVP)
    education_degree = StringField('Degree')
    education_school = StringField('School/University')
    education_year = StringField('Graduation Year')

    # Experience (Simplified: Job 1)
    job_title = StringField('Job Title')
    company = StringField('Company')
    job_description = TextAreaField('Job Description', render_kw={"rows": 5})

    # Skills
    skills = TextAreaField('Skills (comma separated)')

    submit = SubmitField('Generate Resume PDF')


class LinkedInBuilderForm(FlaskForm):
    current_role = StringField(
        'Current Role/Title', validators=[DataRequired()])
    skills = TextAreaField('Key Skills (comma separated)',
                           validators=[DataRequired()])
    achievements = TextAreaField(
        'Key Achievements/Highlights', render_kw={"rows": 5}, validators=[DataRequired()])
    submit = SubmitField('Generate Profile Content')
