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
                    "model_name": "ASTOR Mini",
                    "slug": "astor-mini",
                    "description": "Компактный сервер начального уровня для небольших веб- и внутренних приложений.",
                    "price": 39999.00,
                    "specifications": {
                        "CPU": "4-core 2.0 GHz Intel Xeon E-2224",
                        "RAM": "16 GB DDR4 ECC",
                        "Storage": "2 × 1 TB SATA HDD RAID 1",
                        "Network": "1 × 1 GbE",
                        "Power Supply": "300 W",
                        "Form Factor": "1U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/K5FWGxjS5eR1rLKz9NpBPdPLi1KVMju_4NEJuZQ0OJw/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/1f923322-7ecd-4217-90fa-2071c812eb60.jpg",
                    "is_available": True,
                    "quantity": 20
                },
                {
                    "model_name": "ASTOR Basic",
                    "slug": "astor-basic",
                    "description": "Бюджетная модель для офисных и малонагруженных задач.",
                    "price": 54999.00,
                    "specifications": {
                        "CPU": "6-core 2.2 GHz Intel Xeon E-2236",
                        "RAM": "32 GB DDR4 ECC",
                        "Storage": "2 × 2 TB SATA HDD RAID 1",
                        "Network": "2 × 1 GbE",
                        "Power Supply": "500 W",
                        "Form Factor": "1U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/JW7WNdPSjHL5ScotiwjEFfL8PzQe7s3MnLWrCaAhIHU/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/164d901f-29ed-4285-9ed2-7cf3e41decdf.jpg",
                    "is_available": True,
                    "quantity": 15
                },
                {
                    "model_name": "ASTOR Standard",
                    "slug": "astor-standard",
                    "description": "Универсальный сервер для баз данных среднего масштаба и виртуализации.",
                    "price": 74999.00,
                    "specifications": {
                        "CPU": "8-core 2.6 GHz Intel Xeon E-2276G",
                        "RAM": "64 GB DDR4 ECC",
                        "Storage": "4 × 1 TB SATA HDD RAID 10",
                        "Network": "2 × 10 GbE",
                        "Power Supply": "600 W",
                        "Form Factor": "2U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/ikDUWpOrrWdSnZ9KTLvkLEEas4LnUKkzop5rA3faZmk/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/7030843f-5894-449e-9def-47de992e6bc8.jpg",
                    "is_available": True,
                    "quantity": 12
                },
                {
                    "model_name": "ASTOR Pro",
                    "slug": "astor-pro",
                    "description": "Оптимизированный для кластеров и распределённых вычислений.",
                    "price": 99999.00,
                    "specifications": {
                        "CPU": "12-core 2.8 GHz Intel Xeon Silver 4214",
                        "RAM": "128 GB DDR4 ECC",
                        "Storage": "4 × 960 GB SAS SSD RAID 10",
                        "Network": "2 × 10 GbE",
                        "Power Supply": "800 W",
                        "Form Factor": "2U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/ULPsF8Iqp_DwbwW3TEEs7pISKkeJdr9ZHIfYX48Yo-Q/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/95b15f7f-6192-4163-b43c-85c0ade140ef.jpg",
                    "is_available": True,
                    "quantity": 10
                },
                {
                    "model_name": "ASTOR Ultra",
                    "slug": "astor-ultra",
                    "description": "Высокопроизводительный сервер для HPC и баз данных.",
                    "price": 149999.00,
                    "specifications": {
                        "CPU": "16-core 3.0 GHz Intel Xeon Gold 6230R",
                        "RAM": "256 GB DDR4 ECC",
                        "Storage": "2 × 1 TB NVMe SSD RAID 1",
                        "Network": "2 × 25 GbE",
                        "Power Supply": "1000 W",
                        "Form Factor": "2U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/vYIiiBTDfgjQ_5848UPi5yHYqpbEEJ0gdq9-ZsSTf0E/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/21a4e839-97ec-4e2f-adf2-1daae58f522d.jpg",
                    "is_available": True,
                    "quantity": 8
                },
                {
                    "model_name": "ASTOR ComputeX",
                    "slug": "astor-computex",
                    "description": "Сервер для интенсивных вычислений и ML-задач.",
                    "price": 199999.00,
                    "specifications": {
                        "CPU": "24-core 2.5 GHz AMD EPYC 7352",
                        "RAM": "512 GB DDR4 ECC",
                        "Storage": "4 × 1 TB NVMe SSD RAID 10",
                        "GPU": "2 × NVIDIA T4",
                        "Network": "2 × 25 GbE",
                        "Power Supply": "1200 W",
                        "Form Factor": "2U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/qweyG2gYzksV5BJq5E2KMLi6ALkf73LgFkFsbVDCnTA/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/c2f4aae7-1a11-45e6-bc14-414325f454ae.jpg",
                    "is_available": True,
                    "quantity": 5
                },
                {
                    "model_name": "ASTOR MemoryX",
                    "slug": "astor-memoryx",
                    "description": "Оптимизированный для in-memory баз данных и кэширования.",
                    "price": 249999.00,
                    "specifications": {
                        "CPU": "16-core 3.1 GHz Intel Xeon Gold 6248",
                        "RAM": "1 TB DDR4 ECC",
                        "Storage": "2 × 2 TB NVMe SSD RAID 1",
                        "Network": "4 × 10 GbE",
                        "Power Supply": "1200 W",
                        "Form Factor": "2U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/0YL1OuJ-0nBFLIbxDPfxC4_mPuB0JVt7sHq09NP_AXE/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/2af5910e-7627-467f-9f58-27f1fc23b82b.jpg",
                    "is_available": True,
                    "quantity": 4
                },
                {
                    "model_name": "ASTOR StorageX",
                    "slug": "astor-storagex",
                    "description": "Сетевое хранилище большого объёма для резервного копирования.",
                    "price": 349999.00,
                    "specifications": {
                        "CPU": "8-core 2.2 GHz Intel Xeon Silver 4210",
                        "RAM": "64 GB DDR4 ECC",
                        "Storage": "12 × 4 TB SATA HDD RAID 6",
                        "Network": "4 × 10 GbE",
                        "Power Supply": "800 W",
                        "Form Factor": "4U Storage Chassis"
                    },
                    "image_url": "https://cdn.citilink.ru/g0_BwSG1UNgMx5QwHwlM296OQjiLawP9HuG8AHliXec/resizing_type :fit/gravity:sm/width:400/height:400/plain/product-images/d85a8c91-b39a-487f-9ed0-2c57053dddea.jpg",
                    "is_available": True,
                    "quantity": 3
                },
                {
                    "model_name": "ASTOR Enterprise",
                    "slug": "astor-enterprise",
                    "description": "Топовая конфигурация для крупных дата-центров и суперкомпьютеров.",
                    "price": 499999.00,
                    "specifications": {
                        "CPU": "64-core 2.9 GHz AMD EPYC 7742",
                        "RAM": "2 TB DDR4 ECC",
                        "Storage": "8 × 2 TB NVMe SSD RAID 10",
                        "GPU": "4 × NVIDIA A100",
                        "Network": "8 × 25 GbE",
                        "Power Supply": "2000 W",
                        "Form Factor": "4U Rackmount"
                    },
                    "image_url": "https://cdn.citilink.ru/K5FWGxjS5eR1rLKz9NpBPdPLi1KVMju_4NEJuZQ0OJw/resizing_type:fit/gravity:sm/width:400/height:400/plain/product-images/1f923322-7ecd-4217-90fa-2071c812eb60.jpg",
                    "is_available": True,
                    "quantity": 2
                },
        ]
        for srv in default_servers:
            db.session.add(Server(
                model_name      = srv["model_name"],
                slug            = srv["slug"],
                description     = srv["description"],
                price           = srv["price"],
                specifications  = srv["specifications"],
                image_url       = srv["image_url"],
                is_available    = srv["is_available"],
                quantity        = srv["quantity"]
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
