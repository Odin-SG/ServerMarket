from datetime import datetime
from enum import Enum
from app import db

class OrderStatus(Enum):
    NEW = 'new'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

class ConfigurationType(Enum):
    SOLO = 'Solo'
    SMALL = 'Small'
    MEDIUM = 'Medium'
    LARGE = 'Large'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.NEW, nullable=False)
    configuration = db.Column(db.Enum(ConfigurationType), nullable=False)

    total_price = db.Column(db.Numeric(12,2), nullable=False)
    contact_info = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с позициями заказа
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy='joined')

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(12,2), nullable=False)

    # Сервер можно загрузить при необходимости
    server = db.relationship('Server')