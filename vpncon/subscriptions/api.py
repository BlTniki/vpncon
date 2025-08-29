from flask import Blueprint, jsonify, request
from .crud import get_subscription, create_subscription, update_subscription, delete_subscription, list_subscriptions

bp = Blueprint('subscriptions_api', __name__, url_prefix='/subscriptions')

@bp.route('/', methods=['GET'])
def api_list_subscriptions():
    return jsonify(list_subscriptions())

@bp.route('/<int:sub_id>', methods=['GET'])
def api_get_subscription(sub_id):
    sub = get_subscription(sub_id)
    if sub:
        return jsonify(sub)
    return jsonify({'error': 'Not found'}), 404

@bp.route('/', methods=['POST'])
def api_create_subscription():
    data = request.json
    create_subscription(data['id'], data['price_in_rub'], data['allowed_peers'], data['period'])
    return jsonify({'status': 'created'}), 201

@bp.route('/<int:sub_id>', methods=['PUT'])
def api_update_subscription(sub_id):
    data = request.json
    update_subscription(sub_id, **data)
    return jsonify({'status': 'updated'})

@bp.route('/<int:sub_id>', methods=['DELETE'])
def api_delete_subscription(sub_id):
    delete_subscription(sub_id)
    return jsonify({'status': 'deleted'})
