from flask import (
    render_template, redirect, url_for, flash, request, Blueprint, current_app
)
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderStatus
from app.models.chat_message import ChatMessage
from app.moderator.forms import ChatForm, StatusForm
from app.models.user import UserRole

bp = Blueprint('moderator', __name__, url_prefix='/moderator')


def moderator_required(f):
    from functools import wraps
    from flask import abort
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.role != UserRole.MODERATOR and current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)

    return wrapped


@bp.route('/orders/')
@login_required
@moderator_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()) \
        .paginate(page=page,
                  per_page=current_app.config.get('ITEMS_PER_PAGE', 10),
                  error_out=False)

    return render_template('moderator/orders.html', orders=orders)


@bp.route('/orders/<int:order_id>/', methods=['GET', 'POST'])
@login_required
@moderator_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    chat_form = ChatForm(prefix='chat')
    status_form = StatusForm(prefix='status')
    status_form.status.data = order.status.name

    if chat_form.validate_on_submit() and chat_form.submit.data:
        msg = ChatMessage(
            order_id=order.id,
            user_id=current_user.id,
            message=chat_form.message.data.strip()
        )
        db.session.add(msg)
        db.session.commit()
        flash('Сообщение отправлено', 'success')
        return redirect(url_for('moderator.order_detail', order_id=order.id))

    if status_form.validate_on_submit() and status_form.submit.data:
        new_status = OrderStatus[status_form.status.data]
        order.status = new_status
        db.session.commit()
        flash(f'Статус обновлён на «{new_status.value}»', 'success')
        return redirect(url_for('moderator.order_detail', order_id=order.id))

    chats = order.chat_messages.order_by(ChatMessage.created_at).all()
    return render_template(
        'moderator/order_detail.html',
        order=order,
        chats=chats,
        chat_form=chat_form,
        status_form=status_form
    )


@bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@moderator_required
def order_change_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status_name = request.json.get('status')
    try:
        new_status = OrderStatus[new_status_name]
    except KeyError:
        return {'success': False, 'error': 'Недопустимый статус'}, 400

    order.status = new_status
    db.session.commit()
    return {'success': True, 'new_status': new_status.value}
