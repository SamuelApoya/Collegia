import os
import importlib


def test_config_defaults(monkeypatch):
    # GIVEN
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MAIL_SERVER", raising=False)
    monkeypatch.delenv("MAIL_PORT", raising=False)
    monkeypatch.delenv("MAIL_USERNAME", raising=False)
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)
    monkeypatch.delenv("MAIL_DEFAULT_SENDER", raising=False)

    # WHEN
    config = importlib.import_module("config").Config

    # THEN
    assert config.SECRET_KEY == "dev-secret-key"
    assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///collegia.db"
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert config.MAIL_SERVER == "smtp.gmail.com"
    assert config.MAIL_PORT == 587
    assert config.MAIL_USE_TLS is True
    assert config.MAIL_DEFAULT_SENDER == "noreply@collegia.com"


def test_config_env_overrides(monkeypatch):
    # GIVEN
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("MAIL_SERVER", "smtp.test.com")
    monkeypatch.setenv("MAIL_PORT", "2525")
    monkeypatch.setenv("MAIL_USERNAME", "user@test.com")
    monkeypatch.setenv("MAIL_PASSWORD", "password")
    monkeypatch.setenv("MAIL_DEFAULT_SENDER", "sender@test.com")

    # WHEN
    importlib.reload(importlib.import_module("config"))
    config = importlib.import_module("config").Config

    # THEN
    assert config.SECRET_KEY == "test-secret"
    assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///test.db"
    assert config.MAIL_SERVER == "smtp.test.com"
    assert config.MAIL_PORT == 2525
    assert config.MAIL_USERNAME == "user@test.com"
    assert config.MAIL_PASSWORD == "password"
    assert config.MAIL_DEFAULT_SENDER == "sender@test.com"
