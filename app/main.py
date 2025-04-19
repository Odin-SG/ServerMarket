from flask import Blueprint, render_template
from flask_login import current_user
from app.models.user import User


bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    total_users = User.query.count()

    return render_template('index.html', total_users=total_users)
