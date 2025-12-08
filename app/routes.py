from flask import render_template, redirect, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager
from app.models import User, Meeting, Availability
from forms import LoginForm, RegisterForm, AvailabilityForm, BookingForm

routes = Blueprint("routes", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect("/dashboard")
    return render_template("login.html", form=form)

@routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            return redirect("/register")
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
        open_slots = Availability.query.filter_by(professor_name=current_user.name, booked=False).count()
        booked_sessions = len(meetings)
        return render_template(
            "professor_home.html",
            meetings=meetings,
            slots=slots,
            open_slots=open_slots,
            booked_sessions=booked_sessions,
        )
    else:
        meetings = Meeting.query.filter_by(student=current_user.name).all()
        return render_template("dashboard_student.html", meetings=meetings)

@routes.route("/manage-sessions", methods=["GET", "POST"])
@login_required
def manage_sessions():
    if current_user.role != "professor":
        return redirect("/dashboard")

    form = AvailabilityForm()
    if form.validate_on_submit():
        slot = Availability(
            professor_name=current_user.name,
            date=str(form.date.data),
            time=str(form.time.data)
        )
        db.session.add(slot)
        db.session.commit()
        return redirect("/manage-sessions")

    meetings = Meeting.query.filter_by(professor=current_user.name).all()
    slots = Availability.query.filter_by(professor_name=current_user.name).all()
    return render_template("dashboard_professor.html", form=form, meetings=meetings, slots=slots)

@routes.route("/sessions")
@login_required
def sessions():
    available = Availability.query.filter_by(booked=False).all()
    return render_template("sessions.html", available=available)

@routes.route("/book/<int:slot_id>", methods=["GET", "POST"])
@login_required
def book(slot_id):
    slot = Availability.query.get(slot_id)
    form = BookingForm()

    if form.validate_on_submit():
        meeting = Meeting(
            student=current_user.name,
            professor=slot.professor_name,
            notes=form.notes.data
        )
        slot.booked = True
        db.session.add(meeting)
        db.session.commit()
        return redirect("/dashboard")

    return render_template("book.html", slot=slot, form=form)

@routes.route("/notifications")
@login_required
def notifications():
    if current_user.role == "student":
        data = [
            "New professor time slot available",
            "Session confirmed"
        ]
    else:
        data = [
            "A student booked your session",
            "Your availability is active"
        ]
    return render_template("notifications.html", notifications=data)
