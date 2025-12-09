from flask import Flask
from app.extensions import db, login_manager, mail
from app.routes import routes
from config import Config

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app