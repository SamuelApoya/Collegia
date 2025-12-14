import pytest
from forms import LoginForm, RegisterForm, AvailabilityForm, BookingForm, SettingsForm, MeetingNotesForm
from datetime import date, time


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


class TestLoginForm:
    def test_login_form_fields(self, app):
        with app.app_context():
            form = LoginForm()
            assert hasattr(form, 'email')
            assert hasattr(form, 'password')
            assert hasattr(form, 'submit')
    
    def test_login_form_validation_empty(self, app):
        with app.app_context():
            form = LoginForm(data={})
            assert not form.validate()
            assert 'email' in form.errors
            assert 'password' in form.errors
    
    def test_login_form_validation_invalid_email(self, app):
        with app.app_context():
            form = LoginForm(data={'email': 'invalid', 'password': 'password123'})
            assert not form.validate()
    
    def test_login_form_validation_valid(self, app):
        with app.app_context():
            form = LoginForm(data={'email': 'test@example.com', 'password': 'password123'})
            assert form.validate()


class TestRegisterForm:
    def test_register_form_fields(self, app):
        with app.app_context():
            form = RegisterForm()
            assert hasattr(form, 'name')
            assert hasattr(form, 'email')
            assert hasattr(form, 'password')
            assert hasattr(form, 'role')
            assert hasattr(form, 'submit')
    
    def test_register_form_validation_empty(self, app):
        with app.app_context():
            form = RegisterForm(data={})
            assert not form.validate()
    
    def test_register_form_validation_valid(self, app):
        with app.app_context():
            form = RegisterForm(data={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'password123',
                'role': 'student'
            })
            assert form.validate()


class TestAvailabilityForm:
    def test_availability_form_fields(self, app):
        with app.app_context():
            form = AvailabilityForm()
            assert hasattr(form, 'date')
            assert hasattr(form, 'time')
            assert hasattr(form, 'submit')
    
    def test_availability_form_validation_empty(self, app):
        with app.app_context():
            form = AvailabilityForm(data={})
            assert not form.validate()
    
    def test_availability_form_validation_valid(self, app):
        with app.app_context():
            form = AvailabilityForm(data={
                'date': date(2025, 12, 15),
                'time': time(10, 0)
            })
            assert form.validate()


class TestBookingForm:
    def test_booking_form_fields(self, app):
        with app.app_context():
            form = BookingForm()
            assert hasattr(form, 'notes')
            assert hasattr(form, 'submit')
    
    def test_booking_form_validation_empty(self, app):
        with app.app_context():
            form = BookingForm(data={})
            assert not form.validate()
    
    def test_booking_form_validation_valid(self, app):
        with app.app_context():
            form = BookingForm(data={'notes': 'Discuss project'})
            assert form.validate()


class TestSettingsForm:
    def test_settings_form_fields(self, app):
        with app.app_context():
            form = SettingsForm()
            assert hasattr(form, 'name')
            assert hasattr(form, 'new_password')
            assert hasattr(form, 'profile_picture')
            assert hasattr(form, 'submit')
    
    def test_settings_form_optional_fields(self, app):
        with app.app_context():
            form = SettingsForm(data={})
            assert form.validate()
    
    def test_settings_form_with_name(self, app):
        with app.app_context():
            form = SettingsForm(data={'name': 'New Name'})
            assert form.validate()


class TestMeetingNotesForm:
    def test_meeting_notes_form_fields(self, app):
        with app.app_context():
            form = MeetingNotesForm()
            assert hasattr(form, 'meeting_notes')
            assert hasattr(form, 'submit')
    
    def test_meeting_notes_form_validation_valid(self, app):
        with app.app_context():
            form = MeetingNotesForm(data={'meeting_notes': 'Student performed well'})
            assert form.validate()
    
    def test_meeting_notes_form_empty(self, app):
        with app.app_context():
            form = MeetingNotesForm(data={})
            assert form.validate()