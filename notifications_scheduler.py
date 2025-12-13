from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from datetime import datetime, timedelta
import os

from app.extensions import mail, db
from app.models import Meeting, Notification, User


def check_upcoming_meetings(app):
    with app.app_context():
        now = datetime.now()

        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        meetings_24hr = Meeting.query.filter_by(date=tomorrow).all()

        for meeting in meetings_24hr:
            already_sent = Notification.query.filter_by(
                meeting_id=meeting.id,
                type="meeting_reminder_24hr"
            ).first()
            if already_sent:
                continue

            notify_users(meeting, "24hr")

        today = now.strftime("%Y-%m-%d")
        meetings_today = Meeting.query.filter_by(date=today).all()

        for meeting in meetings_today:
            try:
                meeting_time = datetime.strptime(
                    f"{meeting.date} {meeting.time}",
                    "%Y-%m-%d %H:%M:%S"
                )
                hours_until = (meeting_time - now).total_seconds() / 3600

                if 10 <= hours_until <= 14:
                    already_sent = Notification.query.filter_by(
                        meeting_id=meeting.id,
                        type="meeting_reminder_12hr"
                    ).first()
                    if already_sent:
                        continue

                    notify_users(meeting, "12hr")

            except Exception as e:
                pass

        db.session.commit()


def notify_users(meeting, window):
    student = User.query.filter_by(email=meeting.student_email).first()
    professor = User.query.filter_by(email=meeting.professor_email).first()

    if window == "24hr":
        subject = "Meeting Tomorrow Reminder"
    else:
        subject = "Meeting in 12 Hours"

    body = (
        f"Meeting Details:\n\n"
        f"Date: {meeting.date}\n"
        f"Time: {meeting.time}\n"
        f"Professor: {meeting.professor}\n"
        f"Student: {meeting.student}\n\n"
        f"- Collegia Team"
    )

    if student:
        send_email(student.email, subject, body)
        save_notification(student.email, meeting, window)

    if professor:
        send_email(professor.email, subject, body)
        save_notification(professor.email, meeting, window)


def send_email(to_email, subject, body):
    try:
        msg = Message(subject=subject, recipients=[to_email], body=body)
        mail.send(msg)
    except Exception as e:
        pass


def save_notification(email, meeting, window):
    n = Notification(
        user_email=email,
        message=f"Reminder: meeting at {meeting.time}",
        type=f"meeting_reminder_{window}",
        meeting_id=meeting.id
    )
    db.session.add(n)


def start_scheduler(app):
    if os.getenv("DYNO"):
        return
    
    if os.getenv("WERKZEUG_RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        
        scheduler.add_job(
            func=lambda: check_upcoming_meetings(app),
            trigger="interval",
            minutes=2,
            id="meeting_notifications"
        )
        
        scheduler.add_job(
            func=lambda: check_upcoming_meetings(app),
            trigger="date",
            run_date=datetime.now() + timedelta(seconds=5)
        )
        
        scheduler.start()
        print("[SCHEDULER] Running locally (every 2 minutes)")