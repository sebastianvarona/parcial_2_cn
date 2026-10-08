import requests
from flask import Blueprint, request, jsonify, session
from orders.models.order_model import Order, OrderItem
from db.db import db

order_controller = Blueprint('order_controller', __name__)


def _get_products_service_url():
    """Resolve products service URL — static or via Consul."""
    from flask import current_app
    consul_enabled = current_app.config.get('CONSUL_ENABLED', False)

    if consul_enabled:
        consul_host = current_app.config.get('CONSUL_HOST', 'consul')
        consul_port = current_app.config.get('CONSUL_PORT', 8500)
        try:
            resp = requests.get(
                f'http://{consul_host}:{consul_port}/v1/health/service/products?passing',
                timeout=3,
            )
            if resp.ok:
                services = resp.json()
                if services:
                    svc = services[0]['Service']
                    return f"http://{svc['Address']}:{svc['Port']}"
        except Exception:
            pass  # fall through to static URL

    return current_app.config.get('PRODUCTS_SERVICE_URL', 'http://localhost:3002')


@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    user_name = session.get('username')
    user_email = session.get('email')
    if not user_name or not user_email:
        return jsonify({'message': 'Invalid user session'}), 401

    orders = Order.query.filter_by(user_email=user_email) \
                       .order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    user_name = session.get('username')
    user_email = session.get('email')
    if not user_name or not user_email:
        return jsonify({'message': 'Invalid user session'}), 401

    order = Order.query.get_or_404(order_id)
    if order.user_email != user_email:
        return jsonify({'message': 'Order not found'}), 404
    return jsonify(order.to_dict())


@order_controller.route('/api/orders', methods=['POST'])
def create_order():
    user_name = session.get('username')
    user_email = session.get('email')

    # Support both session-based and body-based user info (frontend sends it)
    if not user_name or not user_email:
        data = request.get_json()
        if data:
            user = data.get('user', {})
            user_name = user.get('name') or user.get('username')
            user_email = user.get('email')
            if user_name:
                session['username'] = user_name
            if user_email:
                session['email'] = user_email

    if not user_name or not user_email:
        return jsonify({'message': 'Información de usuario inválida'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Información de productos inválida'}), 400

    products = data.get('products')
    if not products or not isinstance(products, list):
        return jsonify({'message': 'Información de productos inválida'}), 400

    for p in products:
        if not isinstance(p.get('product_id'), (int, float)) or \
           not isinstance(p.get('quantity'), (int, float)) or \
           int(p['quantity']) <= 0:
            return jsonify({'message': 'Información de productos inválida'}), 400
        p['product_id'] = int(p['product_id'])
        p['quantity'] = int(p['quantity'])

    products_url = _get_products_service_url()
    order_items = []
    total = 0.0

    # 1. Consult prices + stock for every product
    for item in products:
        pid = item['product_id']
        try:
            resp = requests.get(f'{products_url}/api/products/{pid}', timeout=5)
            if resp.status_code == 404:
                return jsonify({'message': f'Product {pid} does not exist'}), 404
            if not resp.ok:
                return jsonify({'message': f'Error querying product {pid}'}), 500
        except requests.RequestException:
            return jsonify({'message': 'Products service unavailable'}), 500

        prod = resp.json()
        if prod['quantity'] < item['quantity']:
            return jsonify({
                'message': f'Insufficient inventory for product {pid} '
                           f'(available: {prod["quantity"]}, requested: {item["quantity"]})'
            }), 409

        unit_price = prod['price']
        product_name = prod['name']
        subtotal = unit_price * item['quantity']
        total += subtotal
        order_items.append({
            'product_id': pid,
            'product_name': product_name,
            'quantity': item['quantity'],
            'unit_price': unit_price,
            'subtotal': subtotal,
        })

    # 2. Deduct inventory for every line
    for item in order_items:
        pid = item['product_id']
        try:
            resp = requests.put(
                f'{products_url}/api/products/{pid}/inventory',
                json={'quantity': item['quantity']},
                timeout=5,
            )
            if resp.status_code == 409:
                order_items_failed = [oi['product_id'] for oi in order_items]
                return jsonify({
                    'message': f'Insufficient inventory for product {pid}',
                    'failed_products': order_items_failed,
                }), 409
            if not resp.ok:
                return jsonify({'message': f'Error updating inventory for product {pid}'}), 500
        except requests.RequestException:
            return jsonify({'message': 'Products service unavailable'}), 500

    # 3. Persist order
    order = Order(user_name=user_name, user_email=user_email, total=total)
    db.session.add(order)
    db.session.flush()  # get order.id

    for item in order_items:
        oi = OrderItem(
            product_id=item['product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=item['subtotal'],
        )
        oi.order_id = order.id
        db.session.add(oi)

    db.session.commit()
    return jsonify({
        'message': 'Orden creada exitosamente',
        'order_id': order.id,
        'total': total,
    }), 201


@order_controller.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
