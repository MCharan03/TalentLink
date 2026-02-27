from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User
import re


class PasswordStrength:
    """Custom validator for password strength."""
    def __init__(self, message=None):
        if not message:
            message = 'Password must be at least 8 characters with 1 uppercase letter and 1 digit.'
        self.message = message

    def __call__(self, form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError(self.message)
        if not re.search(r'[A-Z]', password):
            raise ValidationError(self.message)
        if not re.search(r'[0-9]', password):
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(),
        PasswordStrength(),
        EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class EmployerRegistrationForm(FlaskForm):
    email = StringField('Work Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Full Name', validators=[DataRequired(), Length(1, 64)])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Submit Request')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        PasswordStrength(),
        EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
