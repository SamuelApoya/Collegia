from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Email

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
