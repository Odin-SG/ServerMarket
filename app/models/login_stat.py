from datetime import datetime
from app import db
from app.models.user import User


class LoginStat(db.Model):
    __tablename__ = 'login_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    visit_count = db.Column(db.Integer, default=1, nullable=False)

    user = db.relationship('User', backref='login_stats')

    def __repr__(self):
        who = f"user_id={self.user_id}" if self.user_id else "anonymous"
        return f"<LoginStat {who} ip={self.ip_address} ua={self.user_agent[:20]!r} visits={self.visit_count}>"
