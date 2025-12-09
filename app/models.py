from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    google_id = db.Column(db.String(200), unique=True)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_name = db.Column(db.String(120))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    booked = db.Column(db.Boolean, default=False)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(120))
    professor = db.Column(db.String(120))
    notes = db.Column(db.String(500))
