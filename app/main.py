from flask import Blueprint, render_template
from flask_login import current_user
from app.models.user import User


bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    from app.models.server import Server
    servers = Server.query.order_by(Server.model_name).all()
    return render_template('user/catalog/index.html', servers=servers)

