from app import db
from datetime import datetime


class ServerQuestion(db.Model):
    __tablename__ = 'server_question'

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='server_questions')
    server = db.relationship('Server', backref='questions')
    answers = db.relationship('ServerAnswer', backref='question', cascade='all, delete-orphan')
