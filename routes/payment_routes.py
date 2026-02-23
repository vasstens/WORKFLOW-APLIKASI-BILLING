from flask import Blueprint, jsonify, request

payment_routes = Blueprint('payment_routes', __name__)

@payment_routes.route('/payments', methods=['GET'])
def get_payments():
    # Logic to fetch all payments
    return jsonify({'message': 'Fetching all payments'}), 200

@payment_routes.route('/payments', methods=['POST'])
def create_payment():
    # Logic to create a new payment
    payment_data = request.json
    return jsonify({'message': 'Payment created', 'data': payment_data}), 201

@payment_routes.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    # Logic to fetch a single payment by ID
    return jsonify({'message': 'Fetching payment', 'id': payment_id}), 200

@payment_routes.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    # Logic to update payment by ID
    payment_data = request.json
    return jsonify({'message': 'Payment updated', 'id': payment_id, 'data': payment_data}), 200

@payment_routes.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    # Logic to delete payment by ID
    return jsonify({'message': 'Payment deleted', 'id': payment_id}), 204
