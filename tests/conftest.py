import os
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app, db
from app.models.server import Server
from app.models.order import Order, OrderItem, ConfigurationType
from app.models.user import User, UserRole
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app('app.config.Config')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        u = User(
            username='u1',
            email='u1@test',
            password_hash=generate_password_hash('pwd'),
            role=UserRole.USER
        )
        s1 = Server(model_name='S1', slug='s1', description='d', price=10,
                    specifications={}, is_available=True)
        s2 = Server(model_name='S2', slug='s2', description='d', price=20,
                    specifications={}, is_available=True)
        db.session.add_all([u, s1, s2])
        db.session.commit()

        yield app

        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
