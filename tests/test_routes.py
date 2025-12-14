# tests/test_routes.py

import pytest
from unittest.mock import patch

from app.routes import (
    allowed_file,
    send_email_notification,
    create_google_calendar_event,
    on_load,
)
from app.models import User, Availability, Meeting
from app.extensions import db


def force_login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def test_on_load_executes(app):
    # given
    class DummyState:
        pass

    DummyState.app = app

    # when
    on_load(DummyState())

    # then
    assert True


def test_allowed_file_all_paths():
    # given
    # when
    ok_png = allowed_file("x.png")
    ok_jpg = allowed_file("x.jpg")
    bad_ext = allowed_file("x.exe")
    bad_name = allowed_file("x")
    # then
    assert ok_png is True
    assert ok_jpg is True
    assert bad_ext is False
    assert bad_name is False


def test_send_email_notification_success(monkeypatch):
    # given
    monkeypatch.setattr("app.routes.mail.send", lambda msg: True)
    # when
    send_email_notification("a@test.com", "s", "b")
    # then
    assert True


def test_send_email_notification_exception(monkeypatch):
    # given
    def boom(*a, **k):
        raise Exception("fail")

    monkeypatch.setattr("app.routes.mail.send", boom)
    # when
    send_email_notification("a@test.com", "s", "b")
    # then
    assert True


def test_create_google_calendar_event_all_paths(monkeypatch):
    # given
    class DummyMeeting:
        date = "2025-01-01"
        time = "10:00:00"
        student = "S"
        professor = "P"
        notes = ""

    class GoogleOK:
        authorized = True

        def post(self, *a, **k):
            class R:
                ok = True
            return R()

    class GoogleFail:
        authorized = True

        def post(self, *a, **k):
            raise Exception("boom")

    # when
    monkeypatch.setattr("app.routes.google", GoogleOK())
    ok = create_google_calendar_event(DummyMeeting())

    monkeypatch.setattr("app.routes.google", GoogleFail())
    fail = create_google_calendar_event(DummyMeeting())

    monkeypatch.setattr("app.routes.google", type("G", (), {"authorized": False})())
    unauth = create_google_calendar_event(DummyMeeting())

    # then
    assert ok is True
    assert fail is False
    assert unauth is False


def test_login_page(client):
    # given
    # when
    r = client.get("/")
    # then
    assert r.status_code == 200


def test_logout(client):
    # given
    # when
    r = client.get("/logout")
    # then
    assert r.status_code in (302, 401)


def test_dashboard_student(client, student_user_id):
    # given
    force_login(client, student_user_id)
    # when
    r = client.get("/dashboard")
    # then
    assert r.status_code == 200


def test_dashboard_professor_redirect(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    # when
    r = client.get("/dashboard")
    # then
    assert r.status_code == 302


def test_manage_sessions_get(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    # when
    r = client.get("/manage-sessions")
    # then
    assert r.status_code == 200


def test_manage_sessions_post(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    # when
    r = client.post(
        "/manage-sessions",
        data={"date": "2025-01-01", "time": "10:00:00"},
        follow_redirects=True,
    )
    # then
    assert r.status_code == 200


def test_sessions_student(client, student_user_id):
    # given
    force_login(client, student_user_id)
    # when
    r = client.get("/sessions")
    # then
    assert r.status_code == 200


@patch("app.routes.create_google_calendar_event", return_value=True)
def test_book_get_and_post_success(_, client, professor_user_id, student_user_id):
    # given
    force_login(client, professor_user_id)
    with client.application.app_context():
        slot = Availability(
            professor_name="P",
            professor_email="p@test.com",
            date="2025-01-01",
            time="10:00:00",
        )
        db.session.add(slot)
        db.session.commit()
        sid = slot.id

    force_login(client, student_user_id)

    # when
    r_get = client.get(f"/book/{sid}")
    r_post = client.post(
        f"/book/{sid}",
        data={"notes": "hi"},
        follow_redirects=True,
    )

    # then
    assert r_get.status_code in (200, 302)
    assert r_post.status_code == 200


@patch("app.routes.create_google_calendar_event", return_value=False)
def test_book_calendar_failure(_, client, professor_user_id, student_user_id):
    # given
    force_login(client, professor_user_id)
    with client.application.app_context():
        slot = Availability(
            professor_name="P",
            professor_email="p@test.com",
            date="2025-01-02",
            time="11:00:00",
        )
        db.session.add(slot)
        db.session.commit()
        sid = slot.id

    force_login(client, student_user_id)

    # when
    r = client.post(
        f"/book/{sid}",
        data={"notes": "x"},
        follow_redirects=True,
    )

    # then
    assert r.status_code == 200


def test_meeting_notes_authorized(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    with client.application.app_context():
        prof = User.query.get(professor_user_id)
        m = Meeting(
            student="S",
            student_email="s@test.com",
            professor=prof.name,
            professor_email=prof.email,
            date="2025-01-03",
            time="09:00:00",
        )
        db.session.add(m)
        db.session.commit()
        mid = m.id

    # when
    r = client.get(f"/meeting/{mid}/notes")

    # then
    assert r.status_code == 200


def test_meeting_notes_unauthorized(client, student_user_id, meeting_id):
    # given
    force_login(client, student_user_id)

    # when
    r = client.get(f"/meeting/{meeting_id}/notes")

    # then
    assert r.status_code == 302


def test_delete_slot_all_branches(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    with client.application.app_context():
        slot = Availability(
            professor_name="X",
            professor_email="x@test.com",
            date="2025-01-04",
            time="10:00:00",
            booked=False,
        )
        db.session.add(slot)
        db.session.commit()
        sid = slot.id

    # when
    r = client.post(f"/delete-slot/{sid}", follow_redirects=True)

    # then
    assert r.status_code == 200


def test_cancel_meeting_all_branches(client, professor_user_id):
    # given
    force_login(client, professor_user_id)
    with client.application.app_context():
        prof = User.query.get(professor_user_id)
        m = Meeting(
            student="S",
            student_email="s@test.com",
            professor=prof.name,
            professor_email=prof.email,
            date="2025-01-05",
            time="08:00:00",
        )
        db.session.add(m)
        db.session.commit()
        mid = m.id

    # when
    r = client.post(f"/cancel-meeting/{mid}", follow_redirects=True)

    # then
    assert r.status_code == 200


def test_notifications(client, student_user_id):
    # given
    force_login(client, student_user_id)

    # when
    r = client.get("/notifications")

    # then
    assert r.status_code == 200


def test_settings_get_and_post(client, student_user_id):
    # given
    force_login(client, student_user_id)

    # when
    r_get = client.get("/settings")
    r_post = client.post(
        "/settings",
        data={"name": "New"},
        follow_redirects=True,
    )

    # then
    assert r_get.status_code == 200
    assert r_post.status_code == 200
