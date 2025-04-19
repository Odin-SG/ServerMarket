from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.server import Server
from app.servers.forms import ServerForm

bp = Blueprint('servers', __name__, url_prefix='/servers')


@bp.route('/')
def index():
    servers = Server.query.order_by(Server.model_name).all()
    return render_template('servers/index.html', servers=servers)


@bp.route('/<slug>')
def detail(slug):
    server = Server.query.filter_by(slug=slug).first_or_404()
    return render_template('servers/detail.html', server=server)


@bp.route('/<slug>/info')
def info(slug):
    # API для модального окна
    server = Server.query.filter_by(slug=slug, is_available=True).first_or_404()
    return jsonify({
        'id': server.id,
        'model_name': server.model_name,
        'price': float(server.price),
        'image_url': server.image_url,
        'specifications': server.specifications
    })


# Админ-CRUD (только для ADMIN)
@bp.route('/admin/new', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role.name != 'ADMIN':
        flash('Доступ запрещён.', 'danger')
        return redirect(url_for('servers.index'))
    form = ServerForm()
    if form.validate_on_submit():
        server = Server(
            model_name=form.model_name.data,
            slug=form.slug.data,
            description=form.description.data,
            price=form.price.data,
            specifications=json.loads(form.specifications.data) if form.specifications.data else {},
            image_url=form.image_url.data,
            is_available=form.is_available.data
        )
        try:
            db.session.add(server)
            db.session.commit()
            flash('Сервер добавлен.', 'success')
            return redirect(url_for('servers.detail', slug=server.slug))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Ошибка при сохранении.', 'danger')
    return render_template('servers/form.html', form=form, action='Создать')


@bp.route('/admin/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    if current_user.role.name != 'ADMIN':
        flash('Доступ запрещён.', 'danger')
        return redirect(url_for('servers.index'))
    server = Server.query.filter_by(slug=slug).first_or_404()
    form = ServerForm(obj=server)
    if form.validate_on_submit():
        form.populate_obj(server)
        if form.specifications.data:
            server.specifications = json.loads(form.specifications.data)
        try:
            db.session.commit()
            flash('Сервер обновлён.', 'success')
            return redirect(url_for('servers.detail', slug=server.slug))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Ошибка при обновлении.', 'danger')
    return render_template('servers/form.html', form=form, action='Редактировать')


@bp.route('/admin/<slug>/delete', methods=['POST'])
@login_required
def delete(slug):
    if current_user.role.name != 'ADMIN':
        flash('Доступ запрещён.', 'danger')
        return redirect(url_for('servers.index'))
    server = Server.query.filter_by(slug=slug).first_or_404()
    try:
        db.session.delete(server)
        db.session.commit()
        flash('Сервер удалён.', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Ошибка при удалении.', 'danger')
    return redirect(url_for('servers.index'))
