from flask import Flask
from products.controllers.product_controller import product_controller
from db.db import db
from flask_cors import CORS
import consul_registry
import os
import time

app = Flask(__name__)
app.secret_key = 'secret123'
app.config.from_object('config.Config')
db.init_app(app)


def _init_db_with_retry(max_attempts=30, delay=2):
    """Crea tablas y seed data, reintentando mientras la BD termina de
    iniciar (evita la carrera de arranque con el contenedor MySQL)."""
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            with app.app_context():
                db.create_all()
                # Seed products if table is empty
                from products.models.product_model import Product
                if not Product.query.first():
                    products = [
                        Product('Laptop', 1200.00, 10),
                        Product('Mouse', 25.50, 50),
                        Product('Keyboard', 75.00, 30),
                        Product('Monitor', 300.00, 15),
                        Product('Headphones', 80.00, 20),
                    ]
                    db.session.add_all(products)
                    db.session.commit()
                    app.logger.info('Seeded products table')
            return
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            app.logger.warning('DB no disponible (intento %s/%s): %s', attempt, max_attempts, exc)
            time.sleep(delay)
    raise RuntimeError('No se pudo inicializar la base de datos') from last_exc


_init_db_with_retry()

app.register_blueprint(product_controller)
CORS(app, supports_credentials=True)

# Registro en Consul
_service_port = int(os.environ.get('PORT', '3002'))
consul_registry.register_service(app, 'products', _service_port)

if __name__ == '__main__':
    app.run()
