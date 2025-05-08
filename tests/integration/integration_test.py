import json
from app.models.user import User

LOGIN_URL        = '/auth/login'
SERVERS_URL      = '/servers/'
SERVER_SLUG      = 's1'
SERVER_INFO_URL  = f'/servers/{SERVER_SLUG}/info'
ADD_CART_URL     = '/cart/add'
VIEW_CART_URL    = '/cart/'
CHECKOUT_URL     = '/orders/checkout'
ORDERS_INDEX_URL = '/orders/'

def test_full_order_flow(client, app):
    rv = client.post(ADD_CART_URL, json={'server_id': 1, 'quantity': 1})
    assert rv.status_code == 401

    rv = client.post(
        LOGIN_URL,
        data={'username': 'user1', 'password': 'password123'},
        follow_redirects=True
    )
    assert rv.status_code == 200


    with app.app_context():
        u = User.query.filter_by(username='user1').first()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(u.id)
        sess['_fresh']   = True

    rv = client.get(SERVERS_URL)
    assert rv.status_code == 200
    assert 'S1' in rv.data.decode('utf-8')

    rv = client.get(SERVER_INFO_URL)
    assert rv.status_code == 200
    data = rv.get_json()
    required = {'id', 'model_name', 'price', 'total_sold', 'total_revenue', 'orders_count'}
    assert required.issubset(data.keys())

    rv = client.post(ADD_CART_URL, json={'server_id': data['id'], 'quantity': 2})
    assert rv.status_code == 200
    j = rv.get_json()
    assert j['success'] is True
    assert j['cart_count'] == 2

    rv = client.get(VIEW_CART_URL)
    text = rv.data.decode('utf-8')
    assert 'S1' in text and '2' in text

    rv = client.get(CHECKOUT_URL)
    assert rv.status_code == 200
    assert 'Контактная информация' in rv.data.decode('utf-8')

    rv = client.post(
        CHECKOUT_URL,
        data={'contact_info': 'Интеграционный тест'},
        follow_redirects=True
    )
    page = rv.data.decode('utf-8')
    assert 'Детали заказа' in page
    assert '20.00' in page

    rv = client.get(ORDERS_INDEX_URL)
    assert rv.status_code == 200
    page = rv.data.decode('utf-8')
    assert 'Мои заказы' in page
    assert '<td>1</td>' in page

    rv = client.get(SERVER_INFO_URL)
    stats = rv.get_json()
    assert stats['total_sold']   >= 2
    assert stats['orders_count'] >= 1

