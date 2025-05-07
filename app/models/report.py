from datetime import datetime
from app import db
from app.models.user import User
from app.models.server import Server


class ReportUser(db.Model):
    __tablename__ = 'report_user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('pending', 'processing', 'done', 'failed', name='report_status'),
        nullable=False,
        default='pending'
    )
    file_path = db.Column(db.String(255))

    user = db.relationship('User', backref='reports_user')
    data = db.relationship(
        'ReportDataUser',
        backref='report',
        uselist=False,
        cascade='all, delete-orphan'
    )


class ReportDataUser(db.Model):
    __tablename__ = 'report_data_user'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report_user.id', ondelete='CASCADE'), nullable=False)
    total_orders = db.Column(db.Integer, nullable=False, default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    first_order = db.Column(db.DateTime)
    last_order = db.Column(db.DateTime)


class ReportServer(db.Model):
    __tablename__ = 'report_server'

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('pending', 'processing', 'done', 'failed', name='report_status'),
        nullable=False,
        default='pending'
    )
    file_path = db.Column(db.String(255))

    server = db.relationship('Server', backref='reports_server')
    data = db.relationship(
        'ReportDataServer',
        backref='report',
        uselist=False,
        cascade='all, delete-orphan'
    )


class ReportDataServer(db.Model):
    __tablename__ = 'report_data_server'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(
        db.Integer,
        db.ForeignKey('report_server.id', ondelete='CASCADE'),
        nullable=False
    )
    total_sold = db.Column(db.Integer, nullable=False, default=0)
    total_revenue = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    orders_count = db.Column(db.Integer, nullable=False, default=0)
