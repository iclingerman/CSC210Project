from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Calendars, Events, Share, Reset

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddEventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    dow = SelectMultipleField("Day", validators=[DataRequired()], choices=[('Sunday','Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')])
    start = TimeField('Start', validators=[DataRequired()])
    end = TimeField('End', validators=[DataRequired()])
    notification = BooleanField('Email Notifications')
    submit = SubmitField('Add')
        

class AddCalendarForm(FlaskForm):
    name = StringField('Calendar Name', validators=[DataRequired()])
    submit = SubmitField("Create")

class EmailRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Password Reset Email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None or not user.email_confirmed:
            raise ValidationError('Please use a different email address, or use a confirmed email address.')

class PasswordResetForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    code = StringField('Secret Code', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ShareForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Share')

class DeleteCalendarForm(FlaskForm):
    # verifyDelete = IntegerField('verify', validators=[DataRequired()])
    delete = SubmitField("Delete Calendar")

class EditEventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    dow = SelectMultipleField("Day", validators=[DataRequired()], choices=[('Sunday','Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')])
    start = TimeField('Start', validators=[DataRequired()])
    end = TimeField('End', validators=[DataRequired()])
    notification = BooleanField('Email Notifications')
    delete2 = BooleanField('Delete')
    submit2 = SubmitField('Save')


