from flask import Flask, render_template, request, Response
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
app.secret_key = 'secret123'
CORS(app, supports_credentials=True)
app.config.from_object('config.Config')

USERS_SERVICE = os.environ.get('USERS_SERVICE_URL', 'http://192.168.100.3')
PRODUCTS_SERVICE = os.environ.get('PRODUCTS_SERVICE_URL', 'http://192.168.100.3')
ORDERS_SERVICE = os.environ.get('ORDERS_SERVICE_URL', 'http://192.168.100.3')


def _proxy(url, method='GET'):
    """Forward request to microservice, passing through cookies and body."""
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    data = request.get_data()
    resp = requests.request(
        method=method,
        url=url,
        headers=headers,
        data=data,
        cookies=request.cookies,
        allow_redirects=False,
        timeout=10,
    )
    excluded = {'transfer-encoding', 'content-encoding', 'connection', 'keep-alive'}
    response = Response(resp.content, resp.status_code)
    for k, v in resp.headers.items():
        if k.lower() not in excluded:
            response.headers[k] = v
    return response


# Template routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/editUser/<string:id>')
def edit_user(id):
    return render_template('editUser.html', id=id)

@app.route('/editProduct/<string:id>')
def edit_product(id):
    return render_template('editProduct.html', id=id)

@app.route('/editOrder/<string:id>')
def edit_order(id):
    return render_template('editOrder.html', id=id)


# API proxy routes — users
@app.route('/api/login', methods=['POST'])
def proxy_login():
    return _proxy(f'{USERS_SERVICE}/api/login', 'POST')

@app.route('/api/users', methods=['GET', 'POST'])
def proxy_users():
    return _proxy(f'{USERS_SERVICE}/api/users', request.method)

@app.route('/api/users/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def proxy_users_path(path):
    return _proxy(f'{USERS_SERVICE}/api/users/{path}', request.method)


# API proxy routes — products
@app.route('/api/products', methods=['GET', 'POST'])
def proxy_products():
    return _proxy(f'{PRODUCTS_SERVICE}/api/products', request.method)

@app.route('/api/products/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def proxy_products_path(path):
    return _proxy(f'{PRODUCTS_SERVICE}/api/products/{path}', request.method)


# API proxy routes — orders
@app.route('/api/orders', methods=['GET', 'POST'])
def proxy_orders():
    return _proxy(f'{ORDERS_SERVICE}/api/orders', request.method)

@app.route('/api/orders/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def proxy_orders_path(path):
    return _proxy(f'{ORDERS_SERVICE}/api/orders/{path}', request.method)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
