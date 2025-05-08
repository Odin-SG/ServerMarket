import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User, UserRole
from app import db

def test_user_defaults(app):
    u = User(
        username='x',
        email='x@x.x',
        password_hash=generate_password_hash('h'),
        role=UserRole.USER
    )
    db.session.add(u)
    db.session.commit()
    u2 = User.query.get(u.id)
    assert u2.is_active is True
    assert u2.role == UserRole.USER

def test_password_hashing_and_check(app):
    raw = 'supersecret'
    u = User(username='test', email='t@t.t', password_hash=generate_password_hash(raw), role=UserRole.USER)
    db.session.add(u)
    db.session.commit()
    u2 = User.query.get(u.id)
    assert check_password_hash(u2.password_hash, raw) is True
    assert check_password_hash(u2.password_hash, 'wrong') is False

def test_is_active_default_without_commit(app):
    u = User(username='y', email='y@y.y', password_hash='h', role=UserRole.USER)
    assert u.is_active is None

def test_role_assignment(app):
    u = User(username='z', email='z@z.z', password_hash='h', role=UserRole.ADMIN)
    db.session.add(u)
    db.session.commit()
    u2 = User.query.get(u.id)
    assert u2.role == UserRole.ADMIN
