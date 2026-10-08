import os


class Config:
    MYSQL_HOST = os.environ.get('ORDERS_DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('ORDERS_DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('ORDERS_DB_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('ORDERS_DB_NAME', 'orders_db')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    PRODUCTS_SERVICE_URL = os.environ.get('PRODUCTS_SERVICE_URL', 'http://products-service:3002')
    CONSUL_ENABLED = os.environ.get('CONSUL_ENABLED', 'false').lower() == 'true'
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'consul')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', '8500'))
