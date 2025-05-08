import json
import pytest
from werkzeug.security import generate_password_hash

from app import db
from app.models.order import Order, ConfigurationType
from app.models.user import User, UserRole
from app.models.server import Server

SERVER_INFO_URL = '/servers/s1/info'
INVALID_SERVER_INFO_URL = '/servers/unknown/info'
ADD_CART_URL = '/cart/add'
REMOVE_CART_URL = '/cart/remove'
MOD_STATUS = lambda oid: f'/moderator/orders/{oid}/status'

@pytest.mark.usefixtures('app', 'client')
class TestApiEndpoints:

    def test_server_info_success(self, client):
        rv = client.get(SERVER_INFO_URL)
        assert rv.status_code == 200
        data = rv.get_json()
        assert {'id','model_name','price','total_sold','total_revenue','orders_count'} <= data.keys()

    def test_server_info_not_found(self, client):
        rv = client.get(INVALID_SERVER_INFO_URL)
        assert rv.status_code == 404

    def test_cart_add_requires_auth(self, client):
        rv = client.post(ADD_CART_URL, json={'server_id': 1, 'quantity': 1})
        assert rv.status_code == 401

    def test_cart_remove_requires_auth(self, client):
        rv = client.post(REMOVE_CART_URL, json={'server_id': 1})
        assert rv.status_code == 401

    def test_moderator_status_unauthenticated(self, client, app):
        with app.app_context():
            o = Order(
                user_id=1,
                configuration=ConfigurationType.SOLO,
                total_price=0,
                contact_info={'text': 'api-test'}
            )
            db.session.add(o)
            db.session.commit()
            oid = o.id

        rv = client.post(MOD_STATUS(oid), json={'status': 'PROCESSING'})
        assert rv.status_code == 302

    def test_moderator_status_forbidden_for_user(self, client):
        rv = client.post('/auth/login', data={'username': 'user1', 'password': 'password123'}, follow_redirects=True)
        assert rv.status_code == 200

        rv = client.post(MOD_STATUS(1), json={'status': 'PROCESSING'})
        assert rv.status_code == 403

    def test_moderator_status_invalid_status(self, client, app):
        with app.app_context():
            mod = User(
                username='mod1',
                email='mod1@test',
                password_hash=generate_password_hash('password123'),
                role=UserRole.MODERATOR
            )
            o = Order(
                user_id=1,
                configuration=ConfigurationType.SOLO,
                total_price=0,
                contact_info={'text': 'api-test'}
            )
            db.session.add_all([mod, o])
            db.session.commit()
            oid = o.id

        rv = client.post('/auth/login', data={'username': 'mod1', 'password': 'password123'}, follow_redirects=True)
        assert rv.status_code == 200

        rv = client.post(MOD_STATUS(oid), json={'status': 'UNKNOWN'})
        assert rv.status_code == 400
        data = rv.get_json()
        assert data['success'] is False and 'error' in data

    def test_moderator_status_success(self, client, app):
        with app.app_context():
            mod = User(
                username='mod2',
                email='mod2@test',
                password_hash=generate_password_hash('password123'),
                role=UserRole.MODERATOR
            )
            o = Order(
                user_id=1,
                configuration=ConfigurationType.SOLO,
                total_price=0,
                contact_info={'text': 'api-test'}
            )
            db.session.add_all([mod, o])
            db.session.commit()
            oid = o.id

        rv = client.post('/auth/login', data={'username': 'mod2', 'password': 'password123'}, follow_redirects=True)
        assert rv.status_code == 200

        rv = client.post(MOD_STATUS(oid), json={'status': 'COMPLETED'})
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True and data['new_status'] == 'completed'
