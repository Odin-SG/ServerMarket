from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import CheckConstraint
from app import db

class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    specifications = db.Column(JSON, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=10)

    __table_args__ = (
        CheckConstraint('quantity >= 0', name='server_quantity_non_negative'),
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f'<Server {self.model_name}>'