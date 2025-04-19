from datetime import datetime
from enum import Enum
from app import db, login_manager
from flask_login import UserMixin


class UserRole(Enum):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    confirmed_at = db.Column(db.DateTime)

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    phone_number = db.Column(db.String(20))
    avatar_url = db.Column(db.String(255))
    address = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #orders = db.relationship('Order', backref='user', lazy='dynamic')
    #chat_messages = db.relationship('ChatMessage', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} ({self.email})>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
