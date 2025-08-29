from flask import Blueprint, jsonify, request
from .crud import get_peer, create_peer, update_peer, delete_peer, list_peers

bp = Blueprint('peers_api', __name__, url_prefix='/peers')

@bp.route('/', methods=['GET'])
def api_list_peers():
    return jsonify(list_peers())

@bp.route('/<int:user_id>/<int:host_id>', methods=['GET'])
def api_get_peer(user_id, host_id):
    peer = get_peer(user_id, host_id)
    if peer:
        return jsonify(peer)
    return jsonify({'error': 'Not found'}), 404

@bp.route('/', methods=['POST'])
def api_create_peer():
    data = request.json
    create_peer(data['user_id'], data['host_id'], data['conf_name'], data['peer_ip'], data['is_activated'])
    return jsonify({'status': 'created'}), 201

@bp.route('/<int:user_id>/<int:host_id>', methods=['PUT'])
def api_update_peer(user_id, host_id):
    data = request.json
    update_peer(user_id, host_id, **data)
    return jsonify({'status': 'updated'})

@bp.route('/<int:user_id>/<int:host_id>', methods=['DELETE'])
def api_delete_peer(user_id, host_id):
    delete_peer(user_id, host_id)
    return jsonify({'status': 'deleted'})
