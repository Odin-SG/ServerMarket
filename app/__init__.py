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

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        code = e.code
        descriptions = {
            400: 'Неверный запрос',
            401: 'Требуется авторизация',
            403: 'Доступ запрещён',
            404: 'Страница не найдена',
            500: 'Внутренняя ошибка сервера'
        }
        message = descriptions.get(code, 'Произошла ошибка')
        return render_template('errors/error.html', code=code, message=message), code

    @app.errorhandler(Exception)
    def handle_exception(e):
        return render_template('errors/error.html', code=500, message='Внутренняя ошибка сервера'), 500

    return app