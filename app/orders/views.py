from flask import Blueprint, render_template, redirect, url_for, flash, request
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

order_bp = Blueprint('orders', __name__, url_prefix='/orders')

@order_bp.route('/')
@login_required
def index():
    print("123")
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/index.html', orders=orders)

@order_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_order():
    form = OrderForm()

    servers = Server.query.filter_by(is_available=True).all()
    choices = [(s.id, s.model_name) for s in servers]
    for subform in form.items:
        subform.server_id.choices = choices

    if request.method == 'POST':
        config = ConfigurationType[form.configuration.data]
        form.items.min_entries = config_slots_map[config]
        form.items.entries = form.items.entries[:config_slots_map[config]]

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            configuration=ConfigurationType[form.configuration.data],
            contact_info={'text': form.contact_info.data},
            total_price=0  # заполним ниже
        )
        total = 0
        for item_form in form.items.entries:
            server = Server.query.get(item_form.server_id.data)
            if not server:
                continue
            quantity = item_form.quantity.data
            unit_price = server.price
            total += unit_price * quantity
            order.items.append(OrderItem(
                server_id=server.id,
                quantity=quantity,
                unit_price=unit_price
            ))
        order.total_price = total

        try:
            db.session.add(order)
            db.session.commit()
            flash('Заказ создан успешно!', 'success')
            return redirect(url_for('orders.show', order_id=order.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Ошибка при создании заказа.', 'danger')

    return render_template('orders/new.html', form=form)

@order_bp.route('/<int:order_id>')
@login_required
def show(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Доступ запрещён.', 'warning')
        return redirect(url_for('orders.index'))
    return render_template('orders/show.html', order=order)