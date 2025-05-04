from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.admin import admin_required
from app.admin.forms import ServerForm
from app.models.server import Server
from app.models.order import Order
from app.models.user import User
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
