from flask import Blueprint, jsonify, request
from .crud import get_user_subscription, create_user_subscription, update_user_subscription, delete_user_subscription, list_users_subscriptions

bp = Blueprint('users_subscriptions_api', __name__, url_prefix='/users_subscriptions')

@bp.route('/', methods=['GET'])
def api_list_users_subscriptions():
    return jsonify(list_users_subscriptions())

@bp.route('/<int:user_id>', methods=['GET'])
def api_get_user_subscription(user_id):
    us = get_user_subscription(user_id)
    if us:
        return jsonify(us)
    return jsonify({'error': 'Not found'}), 404

@bp.route('/', methods=['POST'])
def api_create_user_subscription():
    data = request.json
    create_user_subscription(data['user_id'], data['subscription_id'], data['expiration_date'])
    return jsonify({'status': 'created'}), 201

@bp.route('/<int:user_id>', methods=['PUT'])
def api_update_user_subscription(user_id):
    data = request.json
    update_user_subscription(user_id, **data)
    return jsonify({'status': 'updated'})

@bp.route('/<int:user_id>', methods=['DELETE'])
def api_delete_user_subscription(user_id):
    delete_user_subscription(user_id)
    return jsonify({'status': 'deleted'})
