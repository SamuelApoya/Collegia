from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Optional, EqualTo

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    role = SelectField(choices=[("student", "Student"), ("professor", "Professor")])
    submit = SubmitField("Create Account")

class AvailabilityForm(FlaskForm):
    date = DateField(validators=[DataRequired()])
    time = TimeField(validators=[DataRequired()])
    submit = SubmitField("Add Availability")

class BookingForm(FlaskForm):
    notes = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Book Meeting")

class MeetingNotesForm(FlaskForm):
    meeting_notes = TextAreaField('Meeting Notes', validators=[DataRequired()])
    submit = SubmitField("Save Notes")

class SettingsForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    new_password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField("Update Settings")