from app import create_app, db
from app.models.server import Server

app = create_app('app.config.Config')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if Server.query.count() == 0:
            default_servers = [
                {
                    "model_name": "ASTOR Basic",
                    "slug": "astor-basic",
                    "description": "Бюджетная модель сервера для небольших нагрузок.",
                    "price": 49999.00,
                    "specifications": {
                        "CPU": "4-core 2.2 GHz",
                        "RAM": "16 GB DDR4",
                        "Storage": "2 × 1 TB SATA"
                    },
                    "image_url": "https://example.com/images/astor-basic.png",
                    "is_available": True
                },
                {
                    "model_name": "ASTOR Pro",
                    "slug": "astor-pro",
                    "description": "Средняя модель для кластеров средней мощности.",
                    "price": 89999.00,
                    "specifications": {
                        "CPU": "8-core 2.6 GHz",
                        "RAM": "32 GB DDR4",
                        "Storage": "4 × 1 TB SAS"
                    },
                    "image_url": "https://example.com/images/astor-pro.png",
                    "is_available": True
                },
                {
                    "model_name": "ASTOR Ultra",
                    "slug": "astor-ultra",
                    "description": "Топовая модель для высоких нагрузок и HPC.",
                    "price": 159999.00,
                    "specifications": {
                        "CPU": "16-core 3.0 GHz",
                        "RAM": "64 GB DDR4 ECC",
                        "Storage": "2 × 1 TB NVMe"
                    },
                    "image_url": "https://example.com/images/astor-ultra.png",
                    "is_available": True
                },
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

    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
