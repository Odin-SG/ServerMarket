import traceback
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
ma = Marshmallow()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()


def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    import os
    reports_dir = app.config['REPORTS_FOLDER']
    os.makedirs(reports_dir, exist_ok=True)

    talisman.init_app(app,
                      content_security_policy={
                          'default-src': ["'self'"],
                          'script-src': [
                              "'self'",
                              'https://cdn.socket.io',
                              'https://cdn.jsdelivr.net',
                              "'unsafe-inline'",
                              "'unsafe-eval'"
                          ],
                          'style-src': [
                              "'self'",
                              'https://cdn.jsdelivr.net',
                              "'unsafe-inline'"
                          ],
                          'font-src': [
                              "'self'",
                              'https://cdn.jsdelivr.net',
                          ],
                          'img-src': [
                              "'self'",
                              'data:',
                              'https://cdn.jsdelivr.net',
                              'https://i.ebayimg.com'
                          ],
                          'connect-src': [
                              "'self'",
                              'https://cdn.socket.io',
                              'ws://*'
                          ]
                      },
                      force_https=False
                      )

    limiter.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    ma.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    from . import chat_socket

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.auth.views import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.user.views import bp as user_bp
    app.register_blueprint(user_bp)
    from app.moderator.views import bp as moderator_bp
    app.register_blueprint(moderator_bp)
    from app.admin.views import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.commands import generate_reports
    app.cli.add_command(generate_reports)

    @app.context_processor
    def inject_user_roles():
        from app.models.user import UserRole
        return dict(UserRole=UserRole)

    @app.teardown_request
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.remove()

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        tb = traceback.format_exc()
        return render_template('errors/error.html', code=e.code, message=e.description, error_tb=tb), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        tb = traceback.format_exc()
        return render_template('errors/error.html', code=500, message=str(e), error_tb=tb), 500

    return app