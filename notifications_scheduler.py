from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from app.extensions import mail, db
from app.models import Meeting, Notification, User
from datetime import datetime, timedelta

def check_upcoming_meetings(app):
    """Check for meetings happening in the next 24 hours and send notifications"""
    with app.app_context():
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        upcoming_meetings = Meeting.query.filter_by(date=tomorrow, notified=False).all()
        
        for meeting in upcoming_meetings:
            # Notify student
            student = User.query.filter_by(name=meeting.student).first()
            if student:
                send_email_notification(
                    student.email,
                    "Upcoming Meeting Reminder",
                    f"You have a meeting tomorrow ({meeting.date}) at {meeting.time} with {meeting.professor}"
                )
                
                notification = Notification(
                    user_email=student.email,
                    message=f"Reminder: Meeting tomorrow at {meeting.time} with {meeting.professor}",
                    type="meeting_reminder"
                )
                db.session.add(notification)
            
            # Notify professor
            professor = User.query.filter_by(name=meeting.professor).first()
            if professor:
                send_email_notification(
                    professor.email,
                    "Upcoming Meeting Reminder",
                    f"You have a meeting tomorrow ({meeting.date}) at {meeting.time} with {meeting.student}"
                )
                
                notification = Notification(
                    user_email=professor.email,
                    message=f"Reminder: Meeting tomorrow at {meeting.time} with {meeting.student}",
                    type="meeting_reminder"
                )
                db.session.add(notification)
            
            meeting.notified = True
        
        db.session.commit()

def send_email_notification(to_email, subject, body):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

def start_scheduler(app):
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: check_upcoming_meetings(app),
        trigger="interval",
        hours=24,
        id="check_meetings"
    )
    scheduler.start()