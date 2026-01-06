from typing import Any
from flask import jsonify, request
from vpncon.db import auto_transaction
from .model import Subscription
from ..subscriptions import subscriptions_bp, subscription_service

def to_dict(subscription: Subscription) -> dict[str, Any]:
    return {
            'id': subscription.id,
            'price_in_rub': float(subscription.price_in_rub),
            'allowed_peers': subscription.allowed_peers,
            'period': subscription.period,
            'role': subscription.role.value
        }

@subscriptions_bp.route('/<int:subscription_id>', methods=['GET'])
@auto_transaction()
def api_get_subscription(subscription_id: int):
    subscription = subscription_service.get_subscription(subscription_id)
    if subscription:
        return jsonify(to_dict(subscription))
    return jsonify({'error': 'Subscription not found'}), 404




@subscriptions_bp.route('/by-role', methods=['GET'])
@auto_transaction()
def api_get_subscriptions_by_role():
    role = request.args.get('role')
    if not role:
        return jsonify({'error': 'Role parameter is required'}), 400
    subscriptions = subscription_service.get_subscriptions_by_role(role)
    result: list[dict[str, Any]] = []
    for sub in subscriptions:
        result.append(to_dict(sub))
    return jsonify(result)


@subscriptions_bp.route('/', methods=['POST'])
@auto_transaction()
def api_create_subscription():
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    subscription_service.create_subscription(
        data.get('id'), data.get('price_in_rub'), data.get('allowed_peers'), data.get('period'), data.get('role')
    )
    return jsonify({'status': 'created'}), 201


@subscriptions_bp.route('/<int:subscription_id>', methods=['PUT'])
@auto_transaction()
def api_update_subscription(subscription_id: int):
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    subscription_service.update_subscription(
        subscription_id, data.get('price_in_rub'), data.get('allowed_peers'), data.get('period'), data.get('role')
    )
    return jsonify({'status': 'updated'})


@subscriptions_bp.route('/<int:subscription_id>', methods=['DELETE'])
@auto_transaction()
def api_delete_subscription(subscription_id: int):
    subscription_service.delete_subscription(subscription_id)
    return jsonify({'status': 'deleted'})