import pytest
from app import db
from app.models.order import Order, OrderItem, ConfigurationType
from app.models.user import User, UserRole
from app.models.server import Server
from app.user.views import get_server_stats

def make_order(u, s, qty):
    o = Order(user_id=u.id, configuration=ConfigurationType.SOLO,
              contact_info={'text':''}, total_price=qty * s.price)
    o.items.append(OrderItem(server_id=s.id, quantity=qty, unit_price=s.price))
    db.session.add(o)
    return o

def test_get_server_stats_empty(app):
    s = Server.query.first()
    stats = get_server_stats(s.id)
    assert stats['total_sold'] == 0
    assert stats['orders_count'] == 0
    assert stats['total_revenue'] == 0.0

def test_get_server_stats(app):
    u = User.query.first()
    s = Server.query.filter_by(slug='s1').first()
    make_order(u, s, 2); make_order(u, s, 3)
    db.session.commit()
    stats = get_server_stats(s.id)
    assert stats['total_sold'] == 5
    assert stats['orders_count'] == 2
    assert stats['total_revenue'] == pytest.approx(5 * s.price)

def test_different_servers_independent(app):
    u = User.query.first()
    s1 = Server.query.filter_by(slug='s1').first()
    s2 = Server.query.filter_by(slug='s2').first()
    make_order(u, s1, 1)
    make_order(u, s2, 4)
    db.session.commit()
    stats1 = get_server_stats(s1.id)
    stats2 = get_server_stats(s2.id)
    assert stats1['total_sold'] == 1
    assert stats1['orders_count'] == 1
    assert stats2['total_sold'] == 4
    assert stats2['orders_count'] == 1

def test_multiple_users_orders_count(app):
    u2 = User(username='u2', email='u2@t.test', password_hash='h', role=UserRole.USER)
    db.session.add(u2); db.session.commit()
    s = Server.query.filter_by(slug='s1').first()
    make_order(u2, s, 3)
    db.session.commit()
    stats = get_server_stats(s.id)
    assert stats['orders_count'] == 1
