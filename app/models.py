from app.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(200), unique=True, nullable=True)

    profile_picture = db.Column(
        db.String(200),
        nullable=False,
        default="logo.png"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    professor_name = db.Column(db.String(120), nullable=False)
    professor_email = db.Column(db.String(120), nullable=False)

    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)

    booked = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student = db.Column(db.String(120), nullable=False)
    student_email = db.Column(db.String(120), nullable=False)

    professor = db.Column(db.String(120), nullable=False)
    professor_email = db.Column(db.String(120), nullable=False)

    notes = db.Column(db.String(500))
    meeting_notes = db.Column(db.Text)

    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)

    notified = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_email = db.Column(db.String(120), nullable=False)

    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    is_read = db.Column(db.Boolean, default=False)
    meeting_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
