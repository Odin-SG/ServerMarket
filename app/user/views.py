from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, current_app, session
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.user.forms import OrderForm, CartCheckoutForm, UserSettingsForm
from app.models.order import (
    Order, OrderItem, OrderStatus, ConfigurationType
)
from app.models.server import Server
from app.models.chat_message import ChatMessage
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime

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
    server = Server.query.filter_by(slug=slug).first_or_404()
    stats = get_server_stats(server.id)
    return jsonify({
        'id': server.id,
        'model_name': server.model_name,
        'description': server.description,
        'price': float(server.price),
        'image_url': server.image_url,
        'image_filename': server.image_filename,
        'specifications': server.specifications,
        'total_sold': stats['total_sold'],
        'total_revenue': stats['total_revenue'],
        'orders_count': stats['orders_count'],
        'quantity': server.quantity
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
                sid = int(sid)
                qty = int(qty)
            except (TypeError, ValueError):
                flash(f'Неверные данные в позиции {i + 1}', 'danger')
                break

            srv = Server.query.filter_by(id=sid).with_for_update().first()
            if not srv:
                flash(f'Сервер не найден в позиции {i + 1}', 'danger')
                break

            items_data.append({'server': srv, 'quantity': qty})
            total += float(srv.price) * qty
        else:
            for idx, it in enumerate(items_data):
                if it['server'].quantity < it['quantity']:
                    flash(
                        f'В позиции {idx+1}: на складе осталось только '
                        f'{it["server"].quantity} штук',
                        'warning'
                    )
                    db.session.rollback()
                    return redirect(url_for('user.orders_new', configuration=config_name))

            order = Order(
                user_id=current_user.id,
                configuration=ConfigurationType[config_name],
                contact_info={'text': contact_text},
                total_price=total
            )
            for it in items_data:
                srv = it['server']
                srv.quantity -= it['quantity']
                if srv.quantity == 0:
                    srv.is_available = False

                order.items.append(OrderItem(
                    server_id=srv.id,
                    quantity=it['quantity'],
                    unit_price=srv.price
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


@bp.route('/cart/')
@login_required
def cart_view():
    cart = session.get('cart', {})
    servers = []
    total = 0
    for sid, qty in cart.items():
        srv = Server.query.get(sid)
        if not srv: continue
        line = {'server': srv, 'quantity': qty, 'line_total': float(srv.price) * qty}
        total += line['line_total']
        servers.append(line)
    return render_template('user/cart.html', cart_items=servers, total=total)


@bp.route('/cart/add', methods=['POST'])
def cart_add():
    if not current_user.is_authenticated:
        return jsonify(success=False, login=True), 401

    data = request.get_json() or {}
    sid = data.get('server_id')
    qty = data.get('quantity', 1)
    try:
        sid = int(sid);
        qty = int(qty)
    except (TypeError, ValueError):
        return jsonify(success=False, error='Неверные данные'), 400

    srv = Server.query.get(sid)
    if not srv or not srv.is_available:
        return jsonify(success=False, error='Сервер не найден'), 404

    cart = session.get('cart', {})
    cart[str(sid)] = cart.get(str(sid), 0) + qty
    session['cart'] = cart

    return jsonify(success=True, cart_count=sum(cart.values()))


@bp.route('/cart/remove', methods=['POST'])
def cart_remove():
    if not current_user.is_authenticated:
        return jsonify(success=False, error='login_required'), 401
    data = request.get_json() or {}
    sid = data.get('server_id')
    try:
        sid = str(int(sid))
    except (TypeError, ValueError):
        return jsonify(success=False, error='Неверные данные'), 400

    cart = session.get('cart', {})
    if sid in cart:
        cart.pop(sid)
        session['cart'] = cart
        return jsonify(success=True, cart_count=sum(cart.values()))
    return jsonify(success=False, error='Не в корзине'), 404


@bp.route('/orders/checkout', methods=['GET', 'POST'])
@login_required
def cart_checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Ваша корзина пуста.', 'warning')
        return redirect(url_for('user.catalog_index'))

    items = []
    total = 0
    for sid_str, qty in cart.items():
        try:
            sid = int(sid_str)
        except ValueError:
            continue
        srv = Server.query.get(sid)
        if not srv:
            continue
        line_total = float(srv.price) * qty
        total += line_total
        items.append({'server': srv, 'quantity': qty, 'unit_price': srv.price, 'line_total': line_total})

    form = CartCheckoutForm()
    if form.validate_on_submit():
        contact_text = form.contact_info.data.strip()
        order = Order(
            user_id=current_user.id,
            configuration=ConfigurationType.SOLO,
            contact_info={'text': contact_text},
            total_price=total
        )
        for it in items:
            srv = Server.query.filter_by(id=it['server'].id).with_for_update().first()
            if srv.quantity < it['quantity']:
                flash(f'Недостаточно на складе: {srv.model_name}', 'warning')
                db.session.rollback()
                return redirect(url_for('user.cart_view'))

            srv.quantity -= it['quantity']
            if srv.quantity == 0:
                srv.is_available = False

            order.items.append(OrderItem(
                server_id=srv.id,
                quantity=it['quantity'],
                unit_price=it['unit_price']
            ))
        try:
            db.session.add(order)
            db.session.commit()
            session.pop('cart', None)
            flash('Заказ из корзины создан успешно!', 'success')
            return redirect(url_for('user.orders_show', order_id=order.id))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Ошибка при создании заказа.', 'danger')

    return render_template(
        'user/orders/checkout.html',
        form=form,
        items=items,
        total=total
    )


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UserSettingsForm(
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone_number=current_user.phone_number,
        avatar_url=current_user.avatar_url,
        address=current_user.address
    )
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.avatar_url = form.avatar_url.data
        current_user.address = form.address.data

        if form.change_password.data and form.password.data:
            current_user.password_hash = generate_password_hash(form.password.data)

        db.session.commit()
        flash('Профиль обновлён', 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/settings.html', form=form)


def get_server_stats(server_id):
    sold = db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0)) \
        .filter(OrderItem.server_id == server_id).scalar()
    revenue = db.session.query(func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0)) \
        .filter(OrderItem.server_id == server_id).scalar()
    orders_count = db.session.query(func.count(func.distinct(OrderItem.order_id))) \
        .filter(OrderItem.server_id == server_id).scalar()
    return {
        'total_sold': int(sold),
        'total_revenue': float(revenue),
        'orders_count': int(orders_count),
    }


@bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def orders_cancel(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Нельзя отменить чужой заказ', 'danger')
    elif order.status != OrderStatus.NEW:
        flash('Отменить можно только новый заказ', 'warning')
    else:
        order.status = OrderStatus.CANCELED
        db.session.commit()
        flash('Ваш заказ отменён', 'success')
    return redirect(url_for('user.orders_show', order_id=order_id))


@bp.route('/orders/<int:order_id>/edit-contact', methods=['POST'])
@login_required
def orders_edit_contact(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Нельзя изменить чужой заказ', 'danger')
    elif order.status != OrderStatus.NEW:
        flash('Контакт можно менять только для нового заказа', 'warning')
    else:
        new_contact = request.form.get('contact_info', '').strip()
        if not new_contact:
            flash('Контакт не может быть пустым', 'danger')
        else:
            order.contact_info = {'text': new_contact}
            db.session.commit()
            flash('Контактная информация обновлена', 'success')
    return redirect(url_for('user.orders_show', order_id=order_id))


@bp.route('/reference')
def reference():
    return render_template('reference.html', current_year=datetime.utcnow().year)