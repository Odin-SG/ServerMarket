from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.admin import admin_required
from app.admin.forms import ServerForm, OrderEditForm, ChatMessageEditForm, UserEditForm
from app.models.chat_message import ChatMessage
from app.models.server import Server
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.moderator.forms import ChatForm

import json

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    return render_template('admin/index.html',
                           total_users=total_users,
                           total_orders=total_orders,
                           total_revenue=total_revenue)


@bp.route('/servers/')
@login_required
@admin_required
def servers_index():
    servers = Server.query.order_by(Server.model_name).all()
    return render_template('admin/servers/index.html', servers=servers)


@bp.route('/servers/new', methods=['GET', 'POST'])
@login_required
@admin_required
def servers_new():
    form = ServerForm()
    if form.validate_on_submit():
        specs = json.loads(form.specifications.data) if form.specifications.data else {}
        srv = Server(
            model_name=form.model_name.data,
            slug=form.slug.data,
            description=form.description.data,
            price=form.price.data,
            specifications=specs,
            image_url=form.image_url.data,
            is_available=form.is_available.data
        )
        db.session.add(srv);
        db.session.commit()
        flash('Сервер добавлен', 'success')
        return redirect(url_for('admin.servers_index'))
    return render_template('admin/servers/form.html', form=form, action='Создать')


@bp.route('/servers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def servers_edit(id):
    srv = Server.query.get_or_404(id)
    form = ServerForm(obj=srv)
    form.original_slug = srv.slug

    if not form.is_submitted():
        form.specifications.data = json.dumps(srv.specifications or {}, ensure_ascii=False, indent=2)

    if form.validate_on_submit():
        form.populate_obj(srv)
        if form.specifications.data:
            srv.specifications = json.loads(form.specifications.data)
        db.session.commit()
        flash('Сервер обновлён', 'success')
        return redirect(url_for('admin.servers_index'))
    return render_template('admin/servers/form.html', form=form, action='Редактировать')


@bp.route('/servers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def servers_delete(id):
    srv = Server.query.get_or_404(id)
    db.session.delete(srv);
    db.session.commit()
    flash('Сервер удалён', 'success')
    return redirect(url_for('admin.servers_index'))


@bp.route('/orders/')
@login_required
@admin_required
def orders_index():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders/index.html', orders=orders)


@bp.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def orders_edit(order_id):
    order = Order.query.get_or_404(order_id)

    form = OrderEditForm(
        prefix='order',
        status=order.status.name,
        contact_info=order.contact_info.get('text', '')
    )

    chat_form = ChatForm(prefix='chat')

    if request.method == 'POST':
        if form.validate_on_submit() and form.submit.data:
            order.status = OrderStatus[form.status.data]
            order.contact_info = {'text': form.contact_info.data.strip()}
            db.session.commit()
            flash('Заказ обновлён', 'success')
            return redirect(url_for('admin.orders_index'))

    chat_messages = order.chat_messages.order_by(ChatMessage.created_at).all()
    chat_edit_forms = []
    for msg in chat_messages:
        f = ChatMessageEditForm(prefix=f"edit{msg.id}", message=msg.message)
        chat_edit_forms.append((msg, f))

    return render_template(
        'admin/orders/edit.html',
        order=order,
        form=form,
        chat_form=chat_form,
        chat_edit_forms=chat_edit_forms
    )


@bp.route('/orders/<int:order_id>/chat', methods=['POST'])
@login_required
@admin_required
def admin_chat_add(order_id):
    order = Order.query.get_or_404(order_id)
    form = ChatForm()
    if form.validate_on_submit():
        msg = ChatMessage(
            order_id=order.id,
            user_id=current_user.id,
            message=form.message.data.strip()
        )
        db.session.add(msg)
        db.session.commit()
        flash('Сообщение отправлено', 'success')
    else:
        flash('Ошибка при отправке сообщения', 'danger')
    return redirect(url_for('admin.orders_edit', order_id=order.id))



@bp.route('/chat/<int:msg_id>/edit', methods=['POST'])
@login_required
@admin_required
def chat_edit(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)

    save_name   = f"edit{msg.id}-save"
    delete_name = f"edit{msg.id}-delete"
    text_name   = f"edit{msg.id}-message"

    form_data = request.form

    if delete_name in form_data:
        db.session.delete(msg)
        db.session.commit()
        flash('Сообщение удалено', 'warning')

    elif save_name in form_data:
        new_text = form_data.get(text_name, "").strip()
        if new_text:
            msg.message = new_text
            db.session.commit()
            flash('Сообщение обновлено', 'success')
        else:
            flash('Нельзя сохранить пустое сообщение', 'danger')

    return redirect(url_for('admin.orders_edit', order_id=msg.order_id))


@bp.route('/users/')
@login_required
@admin_required
def users_index():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users/index.html', users=users)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def users_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        avatar_url=user.avatar_url,
        address=user.address,
        role=user.role.name,
        is_active=user.is_active
    )
    if form.validate_on_submit():
        user.username     = form.username.data
        user.email        = form.email.data
        user.first_name   = form.first_name.data
        user.last_name    = form.last_name.data
        user.phone_number = form.phone_number.data
        user.avatar_url   = form.avatar_url.data
        user.address      = form.address.data
        user.role         = UserRole[form.role.data]
        user.is_active    = form.is_active.data
        db.session.commit()
        flash('Пользователь сохранён', 'success')
        return redirect(url_for('admin.users_index'))

    return render_template('admin/users/edit.html', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def users_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя удалить себя', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удалён', 'warning')
    return redirect(url_for('admin.users_index'))