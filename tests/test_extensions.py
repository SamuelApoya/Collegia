import pytest
from app.extensions import db, login_manager, mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


def test_db_instance():
    assert isinstance(db, SQLAlchemy)


def test_login_manager_instance():
    assert isinstance(login_manager, LoginManager)


def test_mail_instance():
    assert isinstance(mail, Mail)


def test_extensions_initialized():
    assert db is not None
    assert login_manager is not None
    assert mail is not None