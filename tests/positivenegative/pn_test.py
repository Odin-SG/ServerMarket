import json
import pytest

LOGIN_URL = '/auth/login'
ADD_CART_URL = '/cart/add'
REMOVE_CART_URL = '/cart/remove'
CART_VIEW_URL = '/cart/'
CHECKOUT_URL = '/orders/checkout'


@pytest.mark.usefixtures('app', 'client')
class TestCartAndCheckoutFlow:

    def test_add_to_cart_without_login(self, client):
        """Негатив: без авторизации добавлять в корзину нельзя"""
        rv = client.post(ADD_CART_URL,
                         data=json.dumps({'server_id': 1, 'quantity': 1}),
                         content_type='application/json')
        assert rv.status_code == 401
        data = rv.get_json()
        assert data.get('login') is True

    def test_full_cart_flow(self, client):
        """Позитив: логин → добавить в корзину → просмотреть → удалить → оформить заказ"""
        rv = client.post(LOGIN_URL,
                         data={'username': 'user1', 'password': 'password123'},
                         follow_redirects=True)
        assert rv.status_code == 200
        assert b'user1' in rv.data

        for sid, qty in [(1, 2), (2, 1)]:
            rv = client.post(ADD_CART_URL,
                             data=json.dumps({'server_id': sid, 'quantity': qty}),
                             content_type='application/json')
            assert rv.status_code == 200
            data = rv.get_json()
            assert data['success'] is True

        rv = client.get(CART_VIEW_URL)
        assert rv.status_code == 200
        page = rv.data.decode('utf-8')
        assert 'S1' in page and 'S2' in page

        rv = client.post(REMOVE_CART_URL,
                         data=json.dumps({'server_id': 1}),
                         content_type='application/json')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True
        rv = client.get(CART_VIEW_URL)
        page = rv.data.decode('utf-8')
        assert 'S1' not in page and 'S2' in page

        rv = client.post(CHECKOUT_URL,
                         data={'contact_info': 'Контактные данные'},
                         follow_redirects=True)
        assert rv.status_code == 200
        page = rv.data.decode('utf-8')
        assert 'Детали заказа' in page or 'Заказ #'.lower() in page.lower()

    def test_remove_from_cart_errors(self, client):
        """Негатив: удаление несуществующего элемента"""
        client.post(LOGIN_URL, data={'username': 'user1', 'password': 'password123'})
        rv = client.post(REMOVE_CART_URL,
                         data=json.dumps({'server_id': 999}),
                         content_type='application/json')
        assert rv.status_code == 404
        data = rv.get_json()
        assert data['success'] is False
        assert 'Не в корзине' in data['error']

    def test_invalid_add_data(self, client):
        """Негатив: неверные данные при добавлении"""
        client.post(LOGIN_URL, data={'username': 'user1', 'password': 'password123'})
        rv = client.post(ADD_CART_URL,
                         data=json.dumps({'server_id': 'abc', 'quantity': 'xyz'}),
                         content_type='application/json')
        assert rv.status_code == 400
        data = rv.get_json()
        assert data['success'] is False
        assert 'Неверные данные' in data['error']
