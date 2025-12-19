from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms.validators import DataRequired
from wtforms import StringField

class ResumeAnalysisForm(FlaskForm):
    resume = FileField('Upload Resume (PDF)', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDFs only!')
    ])
    job_description = TextAreaField('Job Description (Optional)')
    submit = SubmitField('Analyze')

class MockTestForm(FlaskForm):
    topic = StringField('Enter a topic for the test', validators=[DataRequired()])
    submit = SubmitField('Start Test')
