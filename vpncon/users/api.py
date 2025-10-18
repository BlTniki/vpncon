from flask import jsonify, request
from vpncon.db import auto_transaction
from .model import User
from ..users import users_bp, user_service


@users_bp.route('/<int:telegram_id>', methods=['GET'])
@auto_transaction
def api_get_user(telegram_id:int):
    user = user_service.get_user(telegram_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/', methods=['POST'])
@auto_transaction
def api_create_user():
    data = request.json
    user_service.create_user(
        data.get('telegram_id'), data.get('telegram_nick'), data.get('role')
    )
    return jsonify({'status': 'created'}), 201

@users_bp.route('/', methods=['PUT'])
def api_update_user():
    data = request.json
    user_service.update_user(
        data.get('telegram_id'), data.get('telegram_nick'), data.get('role')
    )
    return jsonify({'status': 'updated'})

@users_bp.route('/<int:telegram_id>', methods=['DELETE'])
def api_delete_user(telegram_id:int):
    user_service.delete_user(telegram_id)
    return jsonify({'status': 'deleted'})
