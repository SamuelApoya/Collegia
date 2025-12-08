from flask import Flask
from config import Config
from app.extensions import db, login_manager
import os

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app
