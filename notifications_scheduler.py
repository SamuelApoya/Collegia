from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from app.extensions import mail, db
from app.models import Meeting, Notification, User
from datetime import datetime, timedelta

def check_upcoming_meetings(app):
    """Check for meetings happening in the next 24 hours and send notifications"""
    with app.app_context():
        now = datetime.now()  # Use local time consistently
        
        # Check for meetings 24 hours away
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        meetings_24hr = Meeting.query.filter_by(date=tomorrow, notified=False).all()
        
        print(f"[SCHEDULER] Checking for meetings on {tomorrow}...")
        print(f"[SCHEDULER] Found {len(meetings_24hr)} meetings needing 24hr notification")
        
        for meeting in meetings_24hr:
            # Check if we already sent 24hr notification for this meeting
            existing_notif = Notification.query.filter_by(
                meeting_id=meeting.id,
                type="meeting_reminder"
            ).first()
            
            if existing_notif:
                continue  # Skip - already notified
            
            # Notify student
            student = User.query.filter_by(name=meeting.student).first()
            if student:
                send_email_notification(
                    student.email,
                    "📅 Meeting Tomorrow - 24 Hour Reminder",
                    f"Hi {student.name},\n\nYou have a meeting tomorrow ({meeting.date}) at {meeting.time} with {meeting.professor}.\n\nNotes: {meeting.notes}\n\nSee you there!\n\n- Collegia Team"
                )
                
                notification = Notification(
                    user_email=student.email,
                    message=f"⏰ Reminder: Meeting tomorrow at {meeting.time} with {meeting.professor}",
                    type="meeting_reminder",
                    meeting_id=meeting.id
                )
                db.session.add(notification)
                print(f"[SCHEDULER] ✅ Sent 24hr notification to student: {student.email}")
            
            # Notify professor
            professor = User.query.filter_by(name=meeting.professor).first()
            if professor:
                send_email_notification(
                    professor.email,
                    "📅 Meeting Tomorrow - 24 Hour Reminder",
                    f"Hi Prof. {professor.name},\n\nYou have a meeting tomorrow ({meeting.date}) at {meeting.time} with {meeting.student}.\n\nNotes: {meeting.notes}\n\nSee you there!\n\n- Collegia Team"
                )
                
                notification = Notification(
                    user_email=professor.email,
                    message=f"⏰ Reminder: Meeting tomorrow at {meeting.time} with {meeting.student}",
                    type="meeting_reminder",
                    meeting_id=meeting.id
                )
                db.session.add(notification)
                print(f"[SCHEDULER] ✅ Sent 24hr notification to professor: {professor.email}")
            
            meeting.notified = True
        
        # NEW: Check for meetings 12 hours away (same day meetings)
        twelve_hours_from_now = now + timedelta(hours=12)
        today = twelve_hours_from_now.strftime("%Y-%m-%d")
        
        # Get all meetings today that haven't been notified in the last 12 hours
        meetings_12hr = Meeting.query.filter_by(date=today).all()
        
        print(f"[SCHEDULER] Checking for meetings on {today} (12hr check)...")
        print(f"[SCHEDULER] Found {len(meetings_12hr)} meetings on that date")
        
        for meeting in meetings_12hr:
            # Parse meeting time to check if it's within 12 hours
            try:
                meeting_datetime_str = f"{meeting.date} {meeting.time}"
                meeting_datetime = datetime.strptime(meeting_datetime_str, "%Y-%m-%d %H:%M:%S")
                
                time_until_meeting = meeting_datetime - now
                hours_until = time_until_meeting.total_seconds() / 3600
                
                # Send 12hr reminder if meeting is 10-14 hours away (buffer window)
                if 10 <= hours_until <= 14:
                    # Check if we already sent 12hr notification for this meeting
                    existing_notif_12hr = Notification.query.filter_by(
                        meeting_id=meeting.id,
                        type="meeting_reminder_12hr"
                    ).first()
                    
                    if existing_notif_12hr:
                        continue  # Skip - already notified
                    
                    # Notify student
                    student = User.query.filter_by(name=meeting.student).first()
                    if student:
                        notification = Notification(
                            user_email=student.email,
                            message=f"⚡ Meeting in 12 hours! {meeting.time} with {meeting.professor}",
                            type="meeting_reminder_12hr",
                            meeting_id=meeting.id
                        )
                        db.session.add(notification)
                        print(f"[SCHEDULER] ✅ Sent 12hr notification to student: {student.email}")
                    
                    # Notify professor
                    professor = User.query.filter_by(name=meeting.professor).first()
                    if professor:
                        notification = Notification(
                            user_email=professor.email,
                            message=f"⚡ Meeting in 12 hours! {meeting.time} with {meeting.student}",
                            type="meeting_reminder_12hr",
                            meeting_id=meeting.id
                        )
                        db.session.add(notification)
                        print(f"[SCHEDULER] ✅ Sent 12hr notification to professor: {professor.email}")
            except Exception as e:
                print(f"[SCHEDULER] ⚠️ Error processing meeting time: {e}")
        
        db.session.commit()
        print(f"[SCHEDULER] ✅ Notification check complete at {now}")

def send_email_notification(to_email, subject, body):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
        print(f"[EMAIL] ✅ Sent to {to_email}: {subject}")
    except Exception as e:
        print(f"[EMAIL] ❌ Failed to send email to {to_email}: {e}")
        print(f"[EMAIL] ℹ️ Make sure MAIL_USERNAME and MAIL_PASSWORD are set in .env")

def start_scheduler(app, test_mode=False):
    """Start the background scheduler
    
    Args:
        app: Flask application instance
        test_mode: If True, runs every 2 minutes for testing (default: False)
    """
    scheduler = BackgroundScheduler()
    
    if test_mode:
        # TEST MODE: Run every 2 minutes so you can see it in action
        print("=" * 60)
        print("🔧 SCHEDULER STARTED IN TEST MODE")
        print("=" * 60)
        print("⏰ Checking for meetings every 2 MINUTES (for testing)")
        print("📧 Email notifications: Check your email & in-app notifications")
        print("💡 TIP: Create a meeting for tomorrow to test!")
        print("=" * 60)
        
        scheduler.add_job(
            func=lambda: check_upcoming_meetings(app),
            trigger="interval",
            minutes=2,  # Run every 2 minutes for testing
            id="check_meetings"
        )
    else:
        # PRODUCTION MODE: Run every hour (checks both 24hr and 12hr)
        print("=" * 60)
        print("🚀 SCHEDULER STARTED IN PRODUCTION MODE")
        print("=" * 60)
        print("⏰ Checking for meetings every HOUR")
        print("📧 Sends 24hr and 12hr reminders automatically")
        print("=" * 60)
        
        scheduler.add_job(
            func=lambda: check_upcoming_meetings(app),
            trigger="interval",
            hours=1,  # Run every hour in production
            id="check_meetings"
        )
    
    # Run immediately on startup
    scheduler.add_job(
        func=lambda: check_upcoming_meetings(app),
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=5)
    )
    
    scheduler.start()
    print("✅ Scheduler is running...")