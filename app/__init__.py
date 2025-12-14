import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # --------------------
    # Core config
    # --------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # --------------------
    # Database
    # --------------------
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Heroku fix
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///collegia.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------
    # Mail
    # --------------------
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # --------------------
    # Upload limits
    # --------------------
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

    # --------------------
    # Extensions
    # --------------------
    from app.extensions import db, login_manager, mail

    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "routes.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # --------------------
    # Blueprints
    # --------------------
    from app.routes import routes
    app.register_blueprint(routes)

    # --------------------
    # Create tables
    # --------------------
    with app.app_context():
        db.create_all()

    return app
