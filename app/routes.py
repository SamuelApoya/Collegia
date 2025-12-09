import os
from flask import render_template, redirect, Blueprint, request, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from app.extensions import db, login_manager
from app.models import User, Meeting, Availability, Notification
from forms import LoginForm, RegisterForm, AvailabilityForm, BookingForm

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

routes = Blueprint("routes", __name__)

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="routes.google_callback"
)

@routes.record_once
def on_load(state):
    state.app.register_blueprint(google_bp, url_prefix="/login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/dashboard")

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect("/dashboard")

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
        return redirect("/dashboard")

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
        return redirect("/dashboard")

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

@routes.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "professor":
        meetings = Meeting.query.filter_by(professor=current_user.name).all()
        slots = Availability.query.filter_by(professor_name=current_user.name).all()
        open_slots = sum(1 for s in slots if not s.booked)
        booked_sessions = sum(1 for s in slots if s.booked)
        
        return render_template(
            "professor_home.html",
            meetings=meetings,
            open_slots=open_slots,
            booked_sessions=booked_sessions
        )

    meetings = Meeting.query.filter_by(student=current_user.name).all()
    return render_template("dashboard_student.html", meetings=meetings)

@routes.route("/manage-sessions", methods=["GET", "POST"])
@login_required
def manage_sessions():
    if current_user.role != "professor":
        return redirect("/sessions")
    
    form = AvailabilityForm()

    if form.validate_on_submit():
        slot = Availability(
            professor_name=current_user.name,
            date=str(form.date.data),
            time=str(form.time.data)
        )
        db.session.add(slot)
        db.session.commit()
        
        # Create notification for students
        notification = Notification(
            user_email="all_students",
            message=f"New availability added by {current_user.name}",
            type="new_availability"
        )
        db.session.add(notification)
        db.session.commit()
        
        return redirect("/manage-sessions")

    meetings = Meeting.query.filter_by(professor=current_user.name).all()
    slots = Availability.query.filter_by(professor_name=current_user.name).all()

    return render_template("manage_sessions_professor.html", form=form, meetings=meetings, slots=slots)

@routes.route("/sessions")
@login_required
def sessions():
    available = Availability.query.filter_by(booked=False).all()
    return render_template("manage_sessions_student.html", available=available)

@routes.route("/book/<int:slot_id>", methods=["GET", "POST"])
@login_required
def book(slot_id):
    slot = Availability.query.get(slot_id)
    form = BookingForm()

    if form.validate_on_submit():
        meeting = Meeting(
            student=current_user.name,
            professor=slot.professor_name,
            notes=form.notes.data,
            date=slot.date,
            time=slot.time
        )
        slot.booked = True
        db.session.add(meeting)
        
        # Create notification for professor
        professor = User.query.filter_by(name=slot.professor_name).first()
        if professor:
            notification = Notification(
                user_email=professor.email,
                message=f"{current_user.name} booked your session on {slot.date} at {slot.time}",
                type="booking_confirmation"
            )
            db.session.add(notification)
        
        db.session.commit()
        return redirect("/dashboard")

    return render_template("book.html", slot=slot, form=form)

@routes.route("/notifications")
@login_required
def notifications():
    user_notifications = Notification.query.filter(
        (Notification.user_email == current_user.email) |
        (Notification.user_email == f"all_{current_user.role}s")
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template("notifications.html", notifications=user_notifications)