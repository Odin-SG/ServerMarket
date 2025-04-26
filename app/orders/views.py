from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.orders.forms import OrderForm, OrderItemForm
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
    default_server_id = request.args.get('server_id', type=int)
    form = OrderForm()

    servers = Server.query.filter_by(is_available=True).all()
    choices = [(s.id, s.model_name) for s in servers]

    if request.method == 'POST':
        try:
            config = ConfigurationType[form.configuration.data]
            slots = config_slots_map[config]
        except (KeyError, TypeError):
            slots = 1

        form.items.min_entries = slots

        while len(form.items.entries) < slots:
            form.items.append_entry()

    for subform in form.items.entries:
        subform.server_id.choices = choices

    if request.method == 'GET' and default_server_id:
        form.items.entries[0].server_id.data = default_server_id

    if request.method == 'POST':
        current_app.logger.debug("Request.form = %r", request.form)
        if not form.validate():
            current_app.logger.debug("Form validate() returned False, errors = %r", form.errors)
        else:
            current_app.logger.debug("Form validate() returned True")

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            configuration=ConfigurationType[form.configuration.data],
            contact_info={'text': form.contact_info.data},
            total_price=0
        )
        total = 0
        for item_form in form.items.entries:
            srv = Server.query.get(item_form.server_id.data)
            if not srv:
                continue
            qty = item_form.quantity.data
            total += float(srv.price) * qty
            order.items.append(OrderItem(
                server_id=srv.id,
                quantity=qty,
                unit_price=srv.price
            ))
        order.total_price = total

        try:
            db.session.add(order)
            db.session.commit()
            flash('Заказ создан успешно!', 'success')
            return redirect(url_for('orders.show', order_id=order.id))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Ошибка при создании заказа.', 'danger')

    return render_template('orders/new.html', form=form, servers=Server.query.filter_by(is_available=True).order_by(Server.model_name).all())

@bp.route('/<int:order_id>')
@login_required
def show(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Доступ запрещён.', 'warning')
        return redirect(url_for('orders.index'))
    return render_template('orders/show.html', order=order)
