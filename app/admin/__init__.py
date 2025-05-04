from functools import wraps
from flask import abort
from flask_login import current_user
from app.models.user import UserRole


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)

    return wrapped
