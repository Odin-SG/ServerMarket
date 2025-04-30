from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.orders.forms import OrderForm
from app.models.order import Order, OrderStatus, ConfigurationType, OrderItem
from app.models.server import Server

config_slots_map = {
    ConfigurationType.SOLO: 1,
    ConfigurationType.SMALL: 2,
    ConfigurationType.MEDIUM: 4,
    ConfigurationType.LARGE: 8,
}

bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/')
@login_required
def index():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/index.html', orders=orders)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    servers = Server.query.filter_by(is_available=True).order_by(Server.model_name).all()
    config_choices = [(c.name, c.value) for c in ConfigurationType]
    config_slots_map_js = {ct.name: cnt for ct, cnt in config_slots_map.items()}

    form = OrderForm()
    form.configuration.choices = config_choices

    if form.validate_on_submit():
        config_name = form.configuration.data
        try:
            slots = config_slots_map[ConfigurationType[config_name]]
        except KeyError:
            slots = 1

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
                flash(f'Неверные данные в позиции {i+1}', 'danger')
                return render_template('orders/new.html',
                                       form=form,
                                       servers=servers,
                                       config_choices=config_choices,
                                       selected_config=config_name,
                                       contact_info=contact_text,
                                       config_slots_map=config_slots_map_js)

            srv = Server.query.get(sid)
            if not srv:
                flash(f'Сервер не найден в позиции {i+1}', 'danger')
                return render_template('orders/new.html',
                                       form=form,
                                       servers=servers,
                                       config_choices=config_choices,
                                       selected_config=config_name,
                                       contact_info=contact_text,
                                       config_slots_map=config_slots_map_js)

            total += float(srv.price) * qty
            items_data.append({'server_id': srv.id, 'quantity': qty, 'unit_price': srv.price})

        order = Order(
            user_id=current_user.id,
            configuration=ConfigurationType[config_name],
            contact_info={'text': contact_text},
            total_price=total
        )
        for it in items_data:
            order.items.append(OrderItem(server_id=it['server_id'],
                                         quantity=it['quantity'],
                                         unit_price=it['unit_price']))
        try:
            db.session.add(order)
            db.session.commit()
            flash('Заказ создан успешно!', 'success')
            return redirect(url_for('orders.show', order_id=order.id))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Ошибка при создании заказа.', 'danger')

    else:
        config_name = ConfigurationType.SOLO.name
        contact_text = ''
        if not form.is_submitted():
            form.configuration.data = config_name
            form.contact_info.data = contact_text

    return render_template('orders/new.html',
                           form=form,
                           servers=servers,
                           config_choices=config_choices,
                           selected_config=config_name,
                           contact_info=contact_text,
                           config_slots_map=config_slots_map_js)


@bp.route('/<int:order_id>')
@login_required
def show(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Доступ запрещён.', 'warning')
        return redirect(url_for('orders.index'))
    return render_template('orders/show.html', order=order)
