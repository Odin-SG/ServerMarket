import os
import click
from flask import current_app
from flask.cli import with_appcontext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy import func
from app import db
from app.models.report import ReportUser, ReportDataUser
from app.models.report import ReportServer, ReportDataServer
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.server import Server


@click.command('generate-reports')
@with_appcontext
def generate_reports():
    FONT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'arial.ttf')
    pdfmetrics.registerFont(TTFont('Arial', FONT_PATH))

    pending_u = ReportUser.query.filter_by(status='pending').all()
    click.echo(f"Найдено {len(pending_u)} отчётов по пользователям в статусе pending")
    for rpt in pending_u:
        click.echo(f"Обрабатываю ReportUser id={rpt.id} для User id={rpt.user_id}")
        try:
            rpt.status = 'processing'
            db.session.commit()

            total_orders = Order.query.filter_by(user_id=rpt.user_id).count()
            total_amount = db.session.query(
                func.coalesce(func.sum(Order.total_price), 0)
            ).filter_by(user_id=rpt.user_id).scalar() or 0
            first = Order.query.filter_by(user_id=rpt.user_id) \
                .order_by(Order.created_at).first()
            last = Order.query.filter_by(user_id=rpt.user_id) \
                .order_by(Order.created_at.desc()).first()

            data = rpt.data or ReportDataUser(report=rpt)
            data.total_orders = total_orders
            data.total_amount = total_amount
            data.first_order = first.created_at if first else None
            data.last_order = last.created_at if last else None
            db.session.add(data)
            db.session.commit()

            reports_dir = current_app.config['REPORTS_FOLDER']
            filename = f"user_{rpt.user_id}_{rpt.id}.pdf"
            fullpath = os.path.join(reports_dir, filename)

            user = User.query.get(rpt.user_id)
            c = canvas.Canvas(fullpath, pagesize=letter)
            c.setFont("Arial", 14)
            c.drawString(50, 750, f"Отчёт по пользователю: {user.username if user else rpt.user_id}")
            c.setFont("Arial", 12)
            c.drawString(50, 720, f"Всего заказов: {total_orders}")
            c.drawString(50, 700, f"Общая сумма: {total_amount:.2f} ₽")
            if data.first_order:
                c.drawString(50, 680, f"Первый заказ: {data.first_order.strftime('%d.%m.%Y %H:%M')}")
            if data.last_order:
                c.drawString(50, 660, f"Последний заказ: {data.last_order.strftime('%d.%m.%Y %H:%M')}")
            c.showPage()
            c.save()

            rpt.file_path = filename
            rpt.status = 'done'
            db.session.commit()

            click.echo(f"ReportUser id={rpt.id} готов: {filename}")

        except Exception as e:
            db.session.rollback()
            rpt.status = 'failed'
            db.session.commit()
            click.echo(f"Ошибка при обработке id={rpt.id}: {e}", err=True)

    pending_s = ReportServer.query.filter_by(status='pending').all()
    click.echo(f"Найдено {len(pending_s)} отчётов по серверам в статусе pending")
    for rpt in pending_s:
        click.echo(f"Обрабатываю ReportServer id={rpt.id} для Server id={rpt.server_id}")
        try:
            rpt.status = 'processing'
            db.session.commit()

            sold = db.session.query(
                func.coalesce(func.sum(OrderItem.quantity), 0)
            ).filter(OrderItem.server_id == rpt.server_id).scalar() or 0
            revenue = db.session.query(
                func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0)
            ).filter(OrderItem.server_id == rpt.server_id).scalar() or 0
            orders_count = db.session.query(
                func.count(func.distinct(OrderItem.order_id))
            ).filter(OrderItem.server_id == rpt.server_id).scalar() or 0

            data = rpt.data or ReportDataServer(report=rpt)
            data.total_sold = int(sold)
            data.total_revenue = revenue
            data.orders_count = int(orders_count)
            db.session.add(data)
            db.session.commit()

            filename = f"server_{rpt.server_id}_{rpt.id}.pdf"
            fullpath = os.path.join(current_app.config['REPORTS_FOLDER'], filename)
            server = Server.query.get(rpt.server_id)
            c = canvas.Canvas(fullpath, pagesize=letter)
            c.setFont("Arial", 14)
            c.drawString(50, 750, f"Отчёт по серверу: {server.model_name if server else rpt.server_id}")
            c.setFont("Arial", 12)
            c.drawString(50, 720, f"Всего продано: {sold}")
            c.drawString(50, 700, f"Выручка: {revenue:.2f} ₽")
            c.drawString(50, 680, f"Заказов: {orders_count}")
            c.showPage()
            c.save()

            rpt.file_path = filename
            rpt.status = 'done'
            db.session.commit()
            click.echo(f"ReportServer id={rpt.id} готов: {filename}")

        except Exception as e:
            db.session.rollback()
            rpt.status = 'failed'
            db.session.commit()
            click.echo(f"Ошибка при обработке server rpt id={rpt.id}: {e}", err=True)

    click.echo("Генерация отчётов завершена.")
