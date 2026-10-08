class Config:
    DEBUG = True
    # El frontend (BFF) consume los microservicios a través de HAProxy,
    # que es el punto de entrada único (vm-haproxy:80).
    USERS_SERVICE_URL = 'http://192.168.100.3'
    PRODUCTS_SERVICE_URL = 'http://192.168.100.3'
    ORDERS_SERVICE_URL = 'http://192.168.100.3'
