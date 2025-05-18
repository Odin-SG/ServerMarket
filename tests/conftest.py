import os
import tempfile
import pytest

from app import create_app, db
from app.models.server import Server
from app.models.order import Order, OrderItem, ConfigurationType
from app.models.user import User, UserRole
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    db_fd, db_path = tempfile.mkstemp(prefix="test_integration_", suffix=".sqlite")
    os.close(db_fd)
    uri = f"sqlite:///{db_path}"
    os.environ['DATABASE_URL'] = uri

    app = create_app('app.config.TestingConfig')
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=uri,
        SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'check_same_thread': False}}
    )

    with app.app_context():
        db.create_all()
        u = User(
            username='user1',
            email='u1@test',
            password_hash=generate_password_hash('password123'),
            role=UserRole.USER
        )
        s1 = Server(model_name='S1', slug='s1', description='d', price=10,
                    specifications={}, is_available=True)
        s2 = Server(model_name='S2', slug='s2', description='d', price=20,
                    specifications={}, is_available=True)
        db.session.add_all([u, s1, s2])
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()
        db.session.remove()
        db.engine.dispose()
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def _conditional_app_context(request, app):
    path = request.fspath.strpath.replace("\\", "/")
    is_unit = any(p in path for p in ("/tests/unit/", "/tests/services/", "/tests/schemas/"))
    if is_unit:
        with app.app_context():
            yield
    else:
        yield
