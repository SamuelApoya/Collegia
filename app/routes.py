import os
from flask import render_template, redirect, Blueprint, request, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_dance.contrib.google import make_google_blueprint, google
from flask_mail import Message
from app.extensions import db, login_manager, mail
from app.models import User, Meeting, Availability, Notification
from forms import LoginForm, RegisterForm, AvailabilityForm, BookingForm, SettingsForm, MeetingNotesForm
from datetime import datetime, timedelta

UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

routes = Blueprint("routes", __name__)

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    redirect_to="routes.google_callback"
)

@routes.record_once
def on_load(state):
    state.app.register_blueprint(google_bp, url_prefix="/login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email_notification(to_email, subject, body):
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
        print(f"[EMAIL] Sent to {to_email}: {subject}")
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to_email}: {e}")

def create_google_calendar_event(meeting):
    try:
        if not google.authorized:
            return False
        
        meeting_datetime = datetime.strptime(f"{meeting.date} {meeting.time}", "%Y-%m-%d %H:%M:%S")
        end_datetime = meeting_datetime + timedelta(hours=1)
        
        event = {
            'summary': f'Advising Meeting: {meeting.student} & {meeting.professor}',
            'description': f'Student Notes: {meeting.notes}',
            'start': {
                'dateTime': meeting_datetime.isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        response = google.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            json=event
        )
        
        return response.ok
    except Exception as e:
        print(f"[CALENDAR] Error creating event: {e}")
        return False

@routes.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/home")

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect("/home")

    return render_template("login.html", form=form)

@routes.route("/google-callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    data = resp.json()

    email = data["email"]
    name = data["name"]

    user = User.query.filter_by(email=email).first()

    if user:
        if not user.role:
            session["google_user"] = {
                "email": email,
                "name": name
            }
            return redirect("/google-role")

        login_user(user)
        return redirect("/home")

    session["google_user"] = {
        "email": email,
        "name": name
    }
    return redirect("/google-role")

@routes.route("/google-role", methods=["GET", "POST"])
def google_role():
    data = session.get("google_user")
    if not data:
        return redirect("/")

    if request.method == "POST":
        role = request.form.get("role")

        user = User.query.filter_by(email=data["email"]).first()

        if user:
            user.role = role
        else:
            user = User(
                name=data["name"],
                email=data["email"],
                password="google",
                role=role
            )
            db.session.add(user)

        db.session.commit()
        login_user(user)
        return redirect("/home")

    return render_template("google_role.html")

@routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template("register.html", form=form)

@routes.route("/logout")
def logout():
    logout_user()
    return redirect("/")

# HOME - Landing page with hero background + all content
@routes.route("/home")
@login_required
def home():
    if current_user.role == "professor":
        meetings = Meeting.query.filter_by(professor=current_user.name).all()
        slots = Availability.query.filter_by(professor_name=current_user.name).all()
        
        for meeting in meetings:
            student = User.query.filter_by(email=meeting.student_email).first()
            meeting.student_picture = student.profile_picture if student else None
        
        available_count = sum(1 for s in slots if not s.booked)
        booked_count = sum(1 for s in slots if s.booked)
        
        return render_template(
            "home_professor.html",
            meetings=meetings,
            slots=slots,
            available_count=available_count,
            booked_count=booked_count
        )
    else:
        meetings = Meeting.query.filter_by(student=current_user.name).all()
        
        for meeting in meetings:
            professor = User.query.filter_by(email=meeting.professor_email).first()
            meeting.professor_picture = professor.profile_picture if professor else None
        
        return render_template("home_student.html", meetings=meetings)

# MANAGE SESSIONS - For professors to add availability
@routes.route("/manage-sessions", methods=["GET", "POST"])
@login_required
def manage_sessions():
    if current_user.role != "professor":
        return redirect("/sessions")
    
    form = AvailabilityForm()

    if form.validate_on_submit():
        slot = Availability(
            professor_name=current_user.name,
            professor_email=current_user.email,
            date=str(form.date.data),
            time=str(form.time.data)
        )
        db.session.add(slot)
        db.session.commit()
        flash('Availability added successfully!', 'success')
        return redirect("/manage-sessions")

    meetings = Meeting.query.filter_by(professor=current_user.name).all()
    slots = Availability.query.filter_by(professor_name=current_user.name).all()
    
    for meeting in meetings:
        student = User.query.filter_by(email=meeting.student_email).first()
        meeting.student_picture = student.profile_picture if student else None
    
    available_count = sum(1 for s in slots if not s.booked)
    booked_count = sum(1 for s in slots if s.booked)

    return render_template(
        "manage_sessions_professor.html", 
        form=form, 
        meetings=meetings, 
        slots=slots,
        available_count=available_count,
        booked_count=booked_count
    )

@routes.route("/sessions")
@login_required
def sessions():
    # Get available slots
    available = Availability.query.filter_by(booked=False).all()
    
    # Add professor info to available slots
    for slot in available:
        professor = User.query.filter_by(email=slot.professor_email).first()
        slot.professor_name = professor.name if professor else 'Professor'
        slot.professor_picture = professor.profile_picture if professor else None
    
    # Get student's booked meetings
    booked = Meeting.query.filter_by(student_email=current_user.email).order_by(Meeting.date.asc(), Meeting.time.asc()).all()
    
    # Add professor info to booked meetings
    for meeting in booked:
        professor = User.query.filter_by(email=meeting.professor_email).first()
        meeting.professor_name = professor.name if professor else 'Professor'
        meeting.professor_picture = professor.profile_picture if professor else None
    
    return render_template("sessions.html", available=available, booked=booked)

@routes.route("/book/<int:slot_id>", methods=["GET", "POST"])
@login_required
def book(slot_id):
    slot = Availability.query.get(slot_id)
    form = BookingForm()

    if form.validate_on_submit():
        meeting = Meeting(
            student=current_user.name,
            student_email=current_user.email,
            professor=slot.professor_name,
            professor_email=slot.professor_email,
            notes=form.notes.data,
            date=slot.date,
            time=slot.time
        )
        slot.booked = True
        db.session.add(meeting)
        
        professor = User.query.filter_by(email=slot.professor_email).first()
        if professor:
            notification = Notification(
                user_email=professor.email,
                message=f"{current_user.name} booked your session on {slot.date} at {slot.time}",
                type="booking_confirmation"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        calendar_created = create_google_calendar_event(meeting)
        if calendar_created:
            flash('Meeting booked and added to your Google Calendar!', 'success')
        else:
            flash('Meeting booked successfully!', 'success')
        
        return redirect("/home")

    return render_template("book.html", slot=slot, form=form)

@routes.route("/meeting/<int:meeting_id>/notes", methods=["GET", "POST"])
@login_required
def meeting_notes(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if current_user.role != "professor" or meeting.professor != current_user.name:
        flash('Unauthorized access', 'error')
        return redirect("/home")
    
    form = MeetingNotesForm()
    
    if form.validate_on_submit():
        meeting.meeting_notes = form.meeting_notes.data
        db.session.commit()
        flash('Meeting notes saved successfully!', 'success')
        return redirect("/manage-sessions")
    
    if meeting.meeting_notes:
        form.meeting_notes.data = meeting.meeting_notes
    
    return render_template("meeting_notes.html", form=form, meeting=meeting)

@routes.route('/delete-slot/<int:slot_id>', methods=['POST'])
@login_required
def delete_slot(slot_id):
    if current_user.role != 'professor':
        flash('Only professors can delete availability slots.', 'error')
        return redirect(url_for('routes.home'))
    
    slot = Availability.query.get_or_404(slot_id)
    
    if slot.professor_name != current_user.name:
        flash('You can only delete your own availability slots.', 'error')
        return redirect(url_for('routes.manage_sessions'))
    
    if slot.booked:
        flash('Cannot delete a booked slot. Please cancel the meeting first.', 'error')
        return redirect(url_for('routes.manage_sessions'))
    
    db.session.delete(slot)
    db.session.commit()
    
    flash(f'Availability slot for {slot.date} at {slot.time} has been deleted.', 'success')
    return redirect(url_for('routes.manage_sessions'))

@routes.route('/cancel-meeting/<int:meeting_id>', methods=['POST'])
@login_required
def cancel_meeting(meeting_id):
    if current_user.role != 'professor':
        flash('Only professors can cancel meetings.', 'error')
        return redirect(url_for('routes.home'))
    
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.professor != current_user.name:
        flash('You can only cancel your own meetings.', 'error')
        return redirect(url_for('routes.manage_sessions'))
    
    student = User.query.filter_by(email=meeting.student_email).first()
    meeting_date = meeting.date
    meeting_time = meeting.time
    student_name = meeting.student
    
    availability_slot = Availability.query.filter_by(
        date=meeting.date,
        time=meeting.time,
        professor_name=meeting.professor
    ).first()
    
    if availability_slot:
        availability_slot.booked = False
    
    Notification.query.filter_by(meeting_id=meeting_id).delete()
    
    db.session.delete(meeting)
    db.session.commit()
    
    if student:
        cancellation_notification = Notification(
            user_email=student.email,
            message=f'Meeting cancelled: {meeting_date} at {meeting_time} with {meeting.professor}',
            type='meeting_cancelled'
        )
        db.session.add(cancellation_notification)
        
        send_email_notification(
            student.email,
            "Meeting Cancelled - Collegia",
            f"Hi {student.name},\n\nYour meeting on {meeting_date} at {meeting_time} with {meeting.professor} has been cancelled.\n\nPlease book another slot if needed.\n\n- Collegia Team"
        )
        
        db.session.commit()
    
    flash(f'Meeting with {student_name} on {meeting_date} at {meeting_time} has been cancelled. Student notified.', 'success')
    return redirect(url_for('routes.manage_sessions'))

@routes.route('/request-cancellation/<int:meeting_id>', methods=['GET', 'POST'])
@login_required
def request_cancellation(meeting_id):
    if current_user.role != 'student':
        flash('Only students can request meeting cancellations.', 'error')
        return redirect(url_for('routes.home'))
    
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.student_email != current_user.email:
        flash('You can only cancel your own meetings.', 'error')
        return redirect(url_for('routes.sessions'))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        
        professor = User.query.filter_by(email=meeting.professor_email).first()
        meeting_date = meeting.date
        meeting_time = meeting.time
        
        # Free up the availability slot
        availability_slot = Availability.query.filter_by(
            date=meeting.date,
            time=meeting.time,
            professor_name=meeting.professor
        ).first()
        
        if availability_slot:
            availability_slot.booked = False
        
        # Delete the meeting
        db.session.delete(meeting)
        db.session.commit()
        
        # Notify professor
        if professor:
            cancellation_notification = Notification(
                user_email=professor.email,
                message=f'{current_user.name} cancelled meeting on {meeting_date} at {meeting_time}. Reason: {reason}',
                type='meeting_cancelled'
            )
            db.session.add(cancellation_notification)
            
            send_email_notification(
                professor.email,
                "Student Meeting Cancellation - Collegia",
                f"Hi {professor.name},\n\n{current_user.name} has cancelled their meeting on {meeting_date} at {meeting_time}.\n\nReason: {reason}\n\nThe time slot is now available for other students.\n\n- Collegia Team"
            )
            
            db.session.commit()
        
        flash('Meeting cancelled successfully. Professor has been notified.', 'success')
        return redirect(url_for('routes.sessions'))
    
    return render_template('request_cancellation.html', meeting=meeting)

@routes.route("/notifications")
@login_required
def notifications():
    user_notifications = Notification.query.filter(
        (Notification.user_email == current_user.email) |
        (Notification.user_email == f"all_{current_user.role}s")
    ).order_by(Notification.created_at.desc()).all()
    
    for notif in user_notifications:
        notif.is_read = True
    db.session.commit()
    
    return render_template("notifications.html", notifications=user_notifications)

@routes.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm()
    
    if form.validate_on_submit():
        if form.name.data:
            current_user.name = form.name.data
        
        if form.new_password.data:
            current_user.password = generate_password_hash(form.new_password.data)
        
        if form.profile_picture.data:
            file = form.profile_picture.data
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file.save(filepath)
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect("/settings")
    
    form.name.data = current_user.name
    
    return render_template("settings.html", form=form)