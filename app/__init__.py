"""Application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name="default"):
    from config import config_map

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Sign in to continue."
    login_manager.login_message_category = "info"

    from app.models import User, Bus, Route, Reservation, Feedback  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    return app
