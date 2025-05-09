#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-a_stor_shop}"

echo "Ждём Postgres на $DB_HOST:$DB_PORT..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
  sleep 2
done

echo "Postgres доступен — инициализируем базу данных..."

python - << 'PYCODE'
import os
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.server import Server
from app.models.user import User, UserRole

cfg = os.getenv('FLASK_CONFIG', 'app.config.DevelopmentConfig')
app = create_app(cfg)
with app.app_context():
    db.create_all()

    if Server.query.count() == 0:
        default_servers = [
            {
                "model_name": "ASTOR Basic",
                "slug": "astor-basic",
                "description": "Бюджетная модель сервера для небольших нагрузок.",
                "price": 49999.00,
                "specifications": {"CPU": "4-core 2.2 GHz", "RAM": "16 GB DDR4", "Storage": "2 × 1 TB SATA"},
                "image_url": "https://i.ebayimg.com/images/g/nS0AAOSw8ZFgEfGJ/s-l640.jpg",
                "is_available": True
            },
            {"model_name": "ASTOR Pro","slug": "astor-pro","description": "Средняя модель для кластеров средней мощности.",
             "price": 89999.00,"specifications": {"CPU": "8-core 2.6 GHz","RAM": "32 GB DDR4","Storage": "4 × 1 TB SAS"},
             "image_url": "https://i.ebayimg.com/images/g/Fk8AAeSwtWFoE4CE/s-l1600.webp","is_available": True},
            {"model_name": "ASTOR Ultra","slug": "astor-ultra","description": "Топовая модель для высоких нагрузок и HPC.",
             "price": 159999.00,"specifications": {"CPU": "16-core 3.0 GHz","RAM": "64 GB DDR4 ECC","Storage": "2 × 1 TB NVMe"},
             "image_url": "https://i.ebayimg.com/images/g/dC0AAeSwEcloE3~w/s-l1600.webp","is_available": True},
            {"model_name": "ASTOR Max","slug": "astor-max","description": "Топовая модель для очень высоких нагрузок и HPC.",
             "price": 249999.00,"specifications": {"CPU": "32-core 3.2 GHz","RAM": "256 GB DDR4 ECC","Storage": "8 × 1 TB NVMe"},
             "image_url": "https://i.ebayimg.com/images/g/qLUAAOSwB0tnrgsI/s-l1600.webp","is_available": True},
        ]
        for srv in default_servers:
            db.session.add(Server(
                model_name=srv["model_name"],
                slug=srv["slug"],
                description=srv["description"],
                price=srv["price"],
                specifications=srv["specifications"],
                image_url=srv["image_url"],
                is_available=srv["is_available"]
            ))
        db.session.commit()
        print("Default servers added.")

    if User.query.count() == 0:
        users = [
            {'username': 'admin',     'email': 'admin@astor.com',     'role': UserRole.ADMIN},
            {'username': 'moderator', 'email': 'mod@astor.com',       'role': UserRole.MODERATOR},
            {'username': 'user',      'email': 'user@astor.com',      'role': UserRole.USER},
        ]
        for u in users:
            pwd = 'password123'
            db.session.add(User(
                username=u['username'],
                email=u['email'],
                password_hash=generate_password_hash(pwd),
                role=u['role']
            ))
        db.session.commit()
        print("Default users added (password123).")

    print("Database initialization complete.")
PYCODE

exit 0
