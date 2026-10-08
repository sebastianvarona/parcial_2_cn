from flask import Blueprint, request, jsonify
from products.models.product_model import Product
from db.db import db

product_controller = Blueprint('product_controller', __name__)


@product_controller.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@product_controller.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(
        name=data['name'],
        price=float(data['price']),
        quantity=int(data['quantity']),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201


@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json
    product.name = data.get('name', product.name)
    product.price = float(data.get('price', product.price))
    product.quantity = int(data.get('quantity', product.quantity))
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})


@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})


@product_controller.route('/api/products/<int:product_id>/inventory', methods=['PUT'])
def update_inventory(product_id):
    """Deduct inventory — internal endpoint called by orders service."""
    product = Product.query.get_or_404(product_id)
    data = request.json
    quantity = int(data.get('quantity', 0))
    if quantity <= 0:
        return jsonify({'message': 'Invalid quantity'}), 400
    if product.quantity < quantity:
        return jsonify({'message': 'Insufficient inventory'}), 409
    product.quantity -= quantity
    db.session.commit()
    return jsonify({'message': 'Inventory updated', 'new_quantity': product.quantity})


@product_controller.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
