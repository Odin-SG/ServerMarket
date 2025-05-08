import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'p@ss_t-r*ing')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = not DEBUG
    REMEMBER_COOKIE_SECURE = not DEBUG
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
            user=os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', 'postgres')),
            pw=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            host=os.environ.get('DB_HOST', '127.0.0.1'),
            port=os.environ.get('DB_PORT', '5432'),
            db=os.environ.get('POSTGRES_DB', os.environ.get('DB_NAME', 'a_stor_shop'))
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    REPORTS_FOLDER = os.environ.get(
        'REPORTS_FOLDER',
        os.path.join(basedir, '..', 'reports')
    )
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@astor.com')
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@127.0.0.1/a_stor_shop_test'
    )
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    pass
