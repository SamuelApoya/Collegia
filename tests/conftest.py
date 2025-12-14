# tests/conftest.py

import os
import sys
import pytest
from werkzeug.security import generate_password_hash

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.extensions import db
from app.models import User, Meeting


@pytest.fixture(autouse=True)
def reset_env():
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_user_id(app):
    with app.app_context():
        u = User(
            name="Student John",
            email="student@example.com",
            password=generate_password_hash("password123"),
            role="student",
        )
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def professor_user_id(app):
    with app.app_context():
        u = User(
            name="Professor Smith",
            email="prof@example.com",
            password=generate_password_hash("password123"),
            role="professor",
        )
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def meeting_id(app, student_user_id, professor_user_id):
    with app.app_context():
        s = User.query.get(student_user_id)
        p = User.query.get(professor_user_id)
        m = Meeting(
            student=s.name,
            student_email=s.email,
            professor=p.name,
            professor_email=p.email,
            notes="Test meeting",
            date="2025-12-15",
            time="10:00:00",
        )
        db.session.add(m)
        db.session.commit()
        return m.id
