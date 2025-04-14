# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# set the login_view to the name of the view function for the login page
login_manager.login_view = 'auth.login' # 'auth' is the blueprint name, 'login' is the function name
login_manager.login_message = 'Please log in to access this page.' 
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    # create the Flask app instance
    app = Flask(__name__)
    # load the config
    app.config.from_object(config_class)

    # initialize the extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # register the blueprints
    from app.routes.auth import bp as auth_bp # assume auth routes are in app/routes/auth.py !!! not created yet
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # registering the main blueprint
    # from app.routes.main import bp as main_bp
    # app.register_blueprint(main_bp)

    # return the app instance
    return app

# 导入模型，确保 SQLAlchemy 能找到它们（放在 create_app 定义之后，避免循环导入）
# from app import models # 假设模型定义在 app/models.py