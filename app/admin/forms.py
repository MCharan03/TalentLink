from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired


class JobPostingForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    is_ai_round_enabled = BooleanField('Enable AI Interview (1st Round)')
    ai_interviewer_name = SelectField('Select AI Recruiter', choices=[
        ('Aura AI', 'Aura AI (Standard)'),
        ('Neuro-Scribe', 'Neuro-Scribe (Technical)'),
        ('The Oracle', 'The Oracle (Behavioral)')
    ], default='Aura AI')
    ai_interview_tone = SelectField('Interviewer Personality / Tone', choices=[
        ('professional', 'Professional & Polished'),
        ('friendly', 'Encouraging & Friendly'),
        ('clinical', 'Clinical & Data-Driven'),
        ('aggressive', 'High-Pressure / Direct')
    ], default='professional')
    submit = SubmitField('Submit Job Posting')
