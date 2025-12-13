from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    google_id = db.Column(db.String(200), unique=True)
    profile_picture = db.Column(db.String(200), default='logo.png')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_name = db.Column(db.String(120))
    professor_email = db.Column(db.String(120))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    booked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(120))
    student_email = db.Column(db.String(120))
    professor = db.Column(db.String(120))
    professor_email = db.Column(db.String(120))
    notes = db.Column(db.String(500))
    meeting_notes = db.Column(db.Text)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    notified = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120))
    message = db.Column(db.String(500))
    type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    meeting_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)