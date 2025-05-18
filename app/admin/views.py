from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required
from app import db
from app.admin import admin_required
from app.admin.forms import ServerForm, OrderEditForm, ChatMessageEditForm, UserEditForm, ReportUserForm, \
    ReportServerForm
from app.models.chat_message import ChatMessage
from app.models.server import Server
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.moderator.forms import ChatForm
from app.models.report import ReportUser, ReportDataUser, ReportServer, ReportDataServer
from app.models.login_stat import LoginStat
import os
from werkzeug.utils import secure_filename
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
            is_available=form.is_available.data,
            image_url=(None if form.use_upload.data else form.image_url.data),
            image_filename=(None),
            quantity=form.quantity.data
        )

        if form.use_upload.data and form.image_file.data:
            f = form.image_file.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            srv.image_filename = filename

        db.session.add(srv)
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
        srv.model_name = form.model_name.data
        srv.slug = form.slug.data
        srv.description = form.description.data
        srv.price = form.price.data
        srv.quantity = form.quantity.data
        srv.is_available = form.is_available.data

        if form.specifications.data:
            srv.specifications = json.loads(form.specifications.data)

        if form.replace_image.data:
            if form.use_upload.data and form.image_file.data:
                f = form.image_file.data
                filename = secure_filename(f.filename)
                f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                srv.image_filename = filename
                srv.image_url = None
            elif not form.use_upload.data:
                srv.image_url = form.image_url.data or None
                srv.image_filename = None

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

    form = OrderEditForm()

    if not form.is_submitted():
        form.status.data = order.status.name
        form.contact_info.data = order.contact_info.get('text', '')

    chat_form = ChatForm(prefix='chat')

    if request.method == 'POST':
        if form.validate_on_submit():
            order.status = OrderStatus[form.status.data]
            order.contact_info = {'text': form.contact_info.data.strip()}
            db.session.commit()
            flash('Заказ обновлён', 'success')
            return redirect(url_for('admin.orders_index'))
        else:
            print(form.form_errors)

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

    save_name = f"edit{msg.id}-save"
    delete_name = f"edit{msg.id}-delete"
    text_name = f"edit{msg.id}-message"

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
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone_number = form.phone_number.data
        user.avatar_url = form.avatar_url.data
        user.address = form.address.data
        user.role = UserRole[form.role.data]
        user.is_active = form.is_active.data
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


@bp.route('/reports/users/', methods=['GET', 'POST'])
@login_required
@admin_required
def reports_users():
    form = ReportUserForm()
    form.user_id.choices = [(u.id, u.username) for u in User.query.order_by(User.username)]
    if form.validate_on_submit():
        rpt = ReportUser(user_id=form.user_id.data)
        db.session.add(rpt)
        db.session.flush()
        rpt.data = ReportDataUser()
        db.session.commit()
        flash('Запрос на отчёт создан.', 'success')
        return redirect(url_for('admin.reports_users'))

    reports = ReportUser.query.order_by(ReportUser.created_at.desc()).all()
    return render_template(
        'admin/reports/users.html',
        form=form,
        reports=reports
    )


@bp.route('/reports/users/<int:report_id>/download')
@login_required
@admin_required
def download_report_user(report_id):
    rpt = ReportUser.query.get_or_404(report_id)
    if rpt.status != 'done' or not rpt.file_path:
        flash('Отчёт пока не готов.', 'warning')
        return redirect(url_for('admin.reports_users'))
    return send_file(
        os.path.join(current_app.config['REPORTS_FOLDER'], rpt.file_path),
        as_attachment=True,
        download_name=f'user_report_{rpt.user_id}_{rpt.id}.pdf'
    )


@bp.route('/reports/servers/', methods=['GET', 'POST'])
@login_required
@admin_required
def reports_servers():
    form = ReportServerForm()
    form.server_id.choices = [(s.id, s.model_name) for s in Server.query.order_by(Server.model_name)]
    if form.validate_on_submit():
        rpt = ReportServer(server_id=form.server_id.data)
        db.session.add(rpt)
        rpt.data = ReportDataServer()
        db.session.commit()
        flash('Запрос на отчёт по серверу создан.', 'success')
        return redirect(url_for('admin.reports_servers'))

    reports = ReportServer.query.order_by(ReportServer.created_at.desc()).all()
    return render_template(
        'admin/reports/servers.html',
        form=form,
        reports=reports
    )


@bp.route('/reports/servers/<int:report_id>/download')
@login_required
@admin_required
def download_report_server(report_id):
    rpt = ReportServer.query.get_or_404(report_id)
    if rpt.status != 'done' or not rpt.file_path:
        flash('Отчёт пока не готов.', 'warning')
        return redirect(url_for('admin.reports_servers'))
    return send_file(
        os.path.join(current_app.config['REPORTS_FOLDER'], rpt.file_path),
        as_attachment=True,
        download_name=f'server_report_{rpt.server_id}_{rpt.id}.pdf'
    )


@bp.route('/stats/logins/')
@login_required
@admin_required
def login_stats():
    stats = LoginStat.query.order_by(LoginStat.last_seen.desc()).all()
    return render_template('admin/stats/logins.html', stats=stats)
