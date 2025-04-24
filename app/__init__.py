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

    talisman.init_app(app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'"],
            'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
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

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.auth.views import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.orders.views import bp as order_bp
    app.register_blueprint(order_bp)
    from app.servers.views import bp as servers_bp
    app.register_blueprint(servers_bp)

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