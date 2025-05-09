# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Unread Share Count Context Processor
    @app.context_processor
    def inject_unread_share_count():
        from app.models import ShareRecord
        if current_user.is_authenticated:
            cnt = ShareRecord.query \
                .filter_by(receiver_id=current_user.id, is_read=False) \
                .count()
        else:
            cnt = 0
        return {'unread_share_count': cnt}

    # Inject the global ShareForm instance
    @app.context_processor
    def inject_share_form():
        from app.forms import ShareForm
        return {'form': ShareForm()}
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import bp as main_bp 
    app.register_blueprint(main_bp)

    return app
