import pytest
import os
from app import create_app
from app.extensions import db


def test_create_app():
    app = create_app()
    assert app is not None
    assert app.name == 'app'


def test_app_config_development():
    app = create_app()
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False


def test_app_config_secret_key():
    os.environ['SECRET_KEY'] = 'test-secret-key'
    app = create_app()
    assert app.config['SECRET_KEY'] == 'test-secret-key'
    del os.environ['SECRET_KEY']


def test_app_config_mail():
    app = create_app()
    assert 'MAIL_SERVER' in app.config
    assert 'MAIL_PORT' in app.config
    assert 'MAIL_USE_TLS' in app.config


def test_app_blueprints_registered():
    app = create_app()
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    assert 'routes' in blueprint_names


def test_app_database_initialization():
    app = create_app()
    with app.app_context():
        assert db.engine is not None


def test_app_template_folder():
    app = create_app()
    assert app.template_folder.endswith('templates')


def test_app_static_folder():
    app = create_app()
    assert app.static_folder.endswith('static')


def test_app_postgres_url_conversion():
    os.environ['DATABASE_URL'] = 'postgres://user:pass@host/db'
    app = create_app()
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql://')
    del os.environ['DATABASE_URL']


def test_app_mail_port_conversion():
    os.environ['MAIL_PORT'] = '465'
    app = create_app()
    assert app.config['MAIL_PORT'] == 465
    del os.environ['MAIL_PORT']


def test_app_mail_tls_boolean():
    os.environ['MAIL_USE_TLS'] = 'False'
    app = create_app()
    assert app.config['MAIL_USE_TLS'] is False
    del os.environ['MAIL_USE_TLS']