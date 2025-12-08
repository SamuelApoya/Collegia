from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    booked = db.Column(db.Boolean, default=False)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(120), nullable=False)
    professor = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.String(500), nullable=False)
