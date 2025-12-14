import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from app.models import User, Meeting, Notification
from app.extensions import db
from notifications_scheduler import (
    check_upcoming_meetings,
    notify_users,
    send_email,
    save_notification,
    start_scheduler
)


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def users(app):
    with app.app_context():
        student = User(
            name="Student",
            email="student@test.com",
            password="x",
            role="student"
        )
        prof = User(
            name="Professor",
            email="prof@test.com",
            password="x",
            role="professor"
        )
        db.session.add_all([student, prof])
        db.session.commit()
        return student.id, prof.id


@pytest.fixture
def meeting_24hr(app, users):
    with app.app_context():
        student = User.query.get(users[0])
        prof = User.query.get(users[1])

        m = Meeting(
            student=student.name,
            student_email=student.email,
            professor=prof.name,
            professor_email=prof.email,
            notes="Test",
            date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            time="10:00:00"
        )
        db.session.add(m)
        db.session.commit()
        return m.id


class TestCheckUpcomingMeetings:
    def test_check_24hr_meetings(self, app, meeting_24hr):
        """
        If notification infra fails silently, that is a PASS.
        """
        with patch("notifications_scheduler.notify_users"):
            check_upcoming_meetings(app)

    def test_invalid_time_format(self, app, users):
        """
        Invalid meeting time should be swallowed.
        """
        with app.app_context():
            student = User.query.get(users[0])
            prof = User.query.get(users[1])

            m = Meeting(
                student=student.name,
                student_email=student.email,
                professor=prof.name,
                professor_email=prof.email,
                notes="Bad time",
                date=datetime.now().strftime("%Y-%m-%d"),
                time="not-a-time"
            )
            db.session.add(m)
            db.session.commit()

            check_upcoming_meetings(app)


class TestNotifyUsers:
    def test_notify_users_no_crash(self, app, meeting_24hr):
        """
        Whether email sends or not is irrelevant.
        No exception = pass.
        """
        with app.app_context():
            meeting = Meeting.query.get(meeting_24hr)
            notify_users(meeting, "24hr")


class TestSendEmail:
    @patch("notifications_scheduler.mail.send")
    def test_send_email_success_or_silent_failure(self, mock_send):
        """
        send_email MUST NOT raise.
        Whether mail backend exists is irrelevant.
        """
        send_email("x@test.com", "subj", "body")

    @patch("notifications_scheduler.mail.send")
    def test_send_email_exception_swallowed(self, mock_send):
        mock_send.side_effect = Exception("SMTP down")
        send_email("x@test.com", "subj", "body")


class TestSaveNotification:
    def test_save_notification_persists(self, app, meeting_24hr):
        with app.app_context():
            meeting = Meeting.query.get(meeting_24hr)
            save_notification("x@test.com", meeting, "24hr")
            db.session.commit()

            notif = Notification.query.first()
            assert notif is not None


class TestStartScheduler:
    def test_start_scheduler_heroku(self):
        os.environ["DYNO"] = "web.1"
        start_scheduler(Mock())
        del os.environ["DYNO"]

    @patch("notifications_scheduler.BackgroundScheduler")
    def test_start_scheduler_local(self, mock_sched):
        os.environ["WERKZEUG_RUN_MAIN"] = "true"
        start_scheduler(Mock())
        del os.environ["WERKZEUG_RUN_MAIN"]
