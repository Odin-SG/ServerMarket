from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.user.forms import OrderForm, ServerForm
from app.models.order import (
    Order, OrderItem, OrderStatus, ConfigurationType
)
from app.models.server import Server
from app.models.chat_message import ChatMessage

bp = Blueprint('user', __name__)

@bp.route('/servers/')
def catalog_index():
    try:
        servers = Server.query.order_by(Server.model_name).all()
    except Exception:
        db.session.rollback()
        servers = []
    return render_template('user/catalog/index.html', servers=servers)


@bp.route('/servers/<slug>')
def catalog_detail(slug):
    server = Server.query.filter_by(slug=slug).first_or_404()
    return render_template('user/catalog/detail.html', server=server)


@bp.route('/servers/<slug>/info')
def catalog_info(slug):
    server = Server.query.filter_by(slug=slug, is_available=True).first_or_404()
    return jsonify({
        'id': server.id,
        'model_name': server.model_name,
        'price': float(server.price),
        'image_url': server.image_url,
        'specifications': server.specifications
    })

config_slots_map = {
    ConfigurationType.SOLO: 1,
    ConfigurationType.SMALL: 2,
    ConfigurationType.MEDIUM: 4,
    ConfigurationType.LARGE: 8,
}


@bp.route('/orders/')
@login_required
def orders_index():
    orders = Order.query.filter_by(user_id=current_user.id) \
                        .order_by(Order.created_at.desc()) \
                        .all()
    return render_template('user/orders/index.html', orders=orders)


@bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def orders_new():
    servers = Server.query.filter_by(is_available=True) \
                          .order_by(Server.model_name) \
                          .all()
    config_choices = [(c.name, c.value) for c in ConfigurationType]
    config_slots_map_js = {c.name: slots for c, slots in config_slots_map.items()}

    form = OrderForm()
    form.configuration.choices = config_choices

    if form.validate_on_submit():
        config_name = form.configuration.data
        slots = config_slots_map.get(ConfigurationType[config_name], 1)
        contact_text = form.contact_info.data.strip()

        total = 0
        items_data = []
        for i in range(slots):
            sid = request.form.get(f'items-{i}-server_id')
            qty = request.form.get(f'items-{i}-quantity')
            try:
                sid = int(sid); qty = int(qty)
            except (TypeError, ValueError):
                flash(f'Неверные данные в позиции {i+1}', 'danger')
                break

            srv = Server.query.get(sid)
            if not srv:
                flash(f'Сервер не найден в позиции {i+1}', 'danger')
                break

            total += float(srv.price) * qty
            items_data.append({
                'server_id': srv.id,
                'quantity': qty,
                'unit_price': srv.price
            })
        else:
            order = Order(
                user_id=current_user.id,
                configuration=ConfigurationType[config_name],
                contact_info={'text': contact_text},
                total_price=total
            )
            for it in items_data:
                order.items.append(OrderItem(
                    server_id=it['server_id'],
                    quantity=it['quantity'],
                    unit_price=it['unit_price']
                ))
            try:
                db.session.add(order)
                db.session.commit()
                flash('Заказ создан успешно!', 'success')
                return redirect(url_for('user.orders_show', order_id=order.id))
            except SQLAlchemyError:
                db.session.rollback()
                flash('Ошибка при создании заказа.', 'danger')

    if not form.configuration.data:
        form.configuration.data = ConfigurationType.SOLO.name
    return render_template(
        'user/orders/new.html',
        form=form,
        servers=servers,
        config_choices=config_choices,
        selected_config=form.configuration.data,
        contact_info=form.contact_info.data or '',
        config_slots_map_js=config_slots_map_js
    )


@bp.route('/orders/<int:order_id>')
@login_required
def orders_show(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Доступ запрещён.', 'warning')
        return redirect(url_for('user.orders_index'))
    chats = order.chat_messages.order_by(ChatMessage.created_at).all()
    return render_template(
        'user/orders/show.html',
        order=order,
        chats=chats
    )
