import os


class Config:
    MYSQL_HOST = os.environ.get('PRODUCTS_DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('PRODUCTS_DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('PRODUCTS_DB_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('PRODUCTS_DB_NAME', 'products_db')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    CONSUL_ENABLED = os.environ.get('CONSUL_ENABLED', 'false').lower() == 'true'
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'consul')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', '8500'))
