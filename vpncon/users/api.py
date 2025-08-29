from flask import Blueprint, jsonify, request
from .crud import get_user, create_user, update_user, delete_user, list_users

bp = Blueprint('users_api', __name__, url_prefix='/users')

@bp.route('/', methods=['GET'])
def api_list_users():
    return jsonify(list_users())

@bp.route('/<int:telegram_id>', methods=['GET'])
def api_get_user(telegram_id):
    user = get_user(telegram_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@bp.route('/', methods=['POST'])
def api_create_user():
    data = request.json
    create_user(data['telegram_id'], data.get('telegram_nick'), data.get('role'))
    return jsonify({'status': 'created'}), 201

@bp.route('/<int:telegram_id>', methods=['PUT'])
def api_update_user(telegram_id):
    data = request.json
    update_user(telegram_id, **data)
    return jsonify({'status': 'updated'})

@bp.route('/<int:telegram_id>', methods=['DELETE'])
def api_delete_user(telegram_id):
    delete_user(telegram_id)
    return jsonify({'status': 'deleted'})
