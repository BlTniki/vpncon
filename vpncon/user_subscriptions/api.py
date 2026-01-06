from typing import Any
from flask import jsonify, request
from vpncon.db import auto_transaction
from .model import UserSubscription
from . import user_subscriptions_bp, user_subscription_service
from ..users.model import User
from ..subscriptions.model import Subscription

def user_to_dict(user: User) -> dict[str, Any]:
    return {
        'telegram_id': user.telegram_id,
        'telegram_nick': user.telegram_nick,
        'role': user.role.value
    }

def subscription_to_dict(subscription: Subscription) -> dict[str, Any]:
    return {
        'id': subscription.id,
        'price_in_rub': float(subscription.price_in_rub),
        'allowed_peers': subscription.allowed_peers,
        'period': subscription.period,
        'role': subscription.role.value
    }

def to_dict(user_subscription: UserSubscription) -> dict[str, Any]:
    return {
        'user': user_to_dict(user_subscription.user),
        'subscription': subscription_to_dict(user_subscription.subscription),
        'expiry_date': user_subscription.expiry_date
    }

@user_subscriptions_bp.route('/<int:telegram_id>', methods=['GET'])
@auto_transaction()
def api_get_user_subscription(telegram_id: int):
    user_subscription = user_subscription_service.get_user_subscription(telegram_id)
    if user_subscription:
        return jsonify(to_dict(user_subscription))
    return jsonify({'error': 'User subscription not found'}), 404

@user_subscriptions_bp.route('/', methods=['POST'])
@auto_transaction()
def api_create_user_subscription():
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    user_subscription_service.create_user_subscription(
        data.get('telegram_id'), data.get('subscription_id'), data.get('expiry_date')
    )
    return jsonify({'status': 'created'}), 201

@user_subscriptions_bp.route('/<int:telegram_id>', methods=['PUT'])
@auto_transaction()
def api_update_user_subscription(telegram_id: int):
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    user_subscription_service.update_user_subscription(
        telegram_id, data.get('subscription_id'), data.get('expiry_date')
    )
    return jsonify({'status': 'updated'})

@user_subscriptions_bp.route('/<int:telegram_id>', methods=['DELETE'])
@auto_transaction()
def api_delete_user_subscription(telegram_id: int):
    user_subscription_service.delete_user_subscription(telegram_id)
    return jsonify({'status': 'deleted'})