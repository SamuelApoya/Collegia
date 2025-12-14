import pytest
from datetime import datetime
from app.models import User, Availability, Meeting, Notification
from app.extensions import db


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session


class TestUser:
    def test_user_creation(self, db_session):
        user = User(
            name="Test User",
            email="test@example.com",
            password="hashed_password",
            role="student"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "student"
        assert user.profile_picture == "logo.png"
        assert isinstance(user.created_at, datetime)
    
    def test_user_unique_email(self, db_session):
        user1 = User(email="unique@example.com", name="User 1", password="pass", role="student")
        user2 = User(email="unique@example.com", name="User 2", password="pass", role="professor")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_google_id(self, db_session):
        user = User(
            name="Google User",
            email="google@example.com",
            password="google",
            role="student",
            google_id="123456789"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.google_id == "123456789"
    
    def test_user_custom_profile_picture(self, db_session):
        user = User(
            name="Custom Pic User",
            email="custom@example.com",
            password="pass",
            role="professor",
            profile_picture="custom.jpg"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.profile_picture == "custom.jpg"


class TestAvailability:
    def test_availability_creation(self, db_session):
        slot = Availability(
            professor_name="Dr. Smith",
            professor_email="smith@example.com",
            date="2025-12-15",
            time="10:00:00"
        )
        db_session.add(slot)
        db_session.commit()
        
        assert slot.id is not None
        assert slot.professor_name == "Dr. Smith"
        assert slot.professor_email == "smith@example.com"
        assert slot.date == "2025-12-15"
        assert slot.time == "10:00:00"
        assert slot.booked is False
        assert isinstance(slot.created_at, datetime)
    
    def test_availability_booked_status(self, db_session):
        slot = Availability(
            professor_name="Dr. Jones",
            professor_email="jones@example.com",
            date="2025-12-16",
            time="14:00:00",
            booked=True
        )
        db_session.add(slot)
        db_session.commit()
        
        assert slot.booked is True


class TestMeeting:
    def test_meeting_creation(self, db_session):
        meeting = Meeting(
            student="John Doe",
            student_email="john@example.com",
            professor="Dr. Smith",
            professor_email="smith@example.com",
            notes="Discuss thesis",
            date="2025-12-15",
            time="10:00:00"
        )
        db_session.add(meeting)
        db_session.commit()
        
        assert meeting.id is not None
        assert meeting.student == "John Doe"
        assert meeting.student_email == "john@example.com"
        assert meeting.professor == "Dr. Smith"
        assert meeting.professor_email == "smith@example.com"
        assert meeting.notes == "Discuss thesis"
        assert meeting.date == "2025-12-15"
        assert meeting.time == "10:00:00"
        assert meeting.notified is False
        assert isinstance(meeting.created_at, datetime)
    
    def test_meeting_with_notes(self, db_session):
        meeting = Meeting(
            student="Jane Doe",
            student_email="jane@example.com",
            professor="Dr. Jones",
            professor_email="jones@example.com",
            notes="Initial notes",
            meeting_notes="Meeting went well",
            date="2025-12-16",
            time="11:00:00"
        )
        db_session.add(meeting)
        db_session.commit()
        
        assert meeting.meeting_notes == "Meeting went well"
    
    def test_meeting_notified_flag(self, db_session):
        meeting = Meeting(
            student="Test Student",
            student_email="student@example.com",
            professor="Test Professor",
            professor_email="prof@example.com",
            notes="Test",
            date="2025-12-17",
            time="12:00:00",
            notified=True
        )
        db_session.add(meeting)
        db_session.commit()
        
        assert meeting.notified is True


class TestNotification:
    def test_notification_creation(self, db_session):
        notif = Notification(
            user_email="user@example.com",
            message="Your meeting is tomorrow",
            type="meeting_reminder_24hr",
            meeting_id=1
        )
        db_session.add(notif)
        db_session.commit()
        
        assert notif.id is not None
        assert notif.user_email == "user@example.com"
        assert notif.message == "Your meeting is tomorrow"
        assert notif.type == "meeting_reminder_24hr"
        assert notif.meeting_id == 1
        assert notif.is_read is False
        assert isinstance(notif.created_at, datetime)
    
    def test_notification_read_status(self, db_session):
        notif = Notification(
            user_email="user@example.com",
            message="Test notification",
            type="booking_confirmation",
            is_read=True
        )
        db_session.add(notif)
        db_session.commit()
        
        assert notif.is_read is True
    
    def test_notification_without_meeting(self, db_session):
        notif = Notification(
            user_email="user@example.com",
            message="General announcement",
            type="announcement"
        )
        db_session.add(notif)
        db_session.commit()
        
        assert notif.meeting_id is None