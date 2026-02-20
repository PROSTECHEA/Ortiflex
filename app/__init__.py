from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.inventory import inventory
    from app.routes.projects import projects
    from app.routes.users import users
    from app.routes.reports import reports

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(inventory)
    app.register_blueprint(projects)
    app.register_blueprint(users)
    app.register_blueprint(reports)

    with app.app_context():
        db.create_all()

    return app
