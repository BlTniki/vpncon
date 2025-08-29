from flask import Blueprint, jsonify, request
from .crud import get_host, create_host, update_host, delete_host, list_hosts

bp = Blueprint('hosts_api', __name__, url_prefix='/hosts')

@bp.route('/', methods=['GET'])
def api_list_hosts():
    return jsonify(list_hosts())

@bp.route('/<int:host_id>', methods=['GET'])
def api_get_host(host_id):
    host = get_host(host_id)
    if host:
        return jsonify(host)
    return jsonify({'error': 'Not found'}), 404

@bp.route('/', methods=['POST'])
def api_create_host():
    data = request.json
    create_host(data['id'], data['name'], data['ipaddres'], data['port'], data['host_password'])
    return jsonify({'status': 'created'}), 201

@bp.route('/<int:host_id>', methods=['PUT'])
def api_update_host(host_id):
    data = request.json
    update_host(host_id, **data)
    return jsonify({'status': 'updated'})

@bp.route('/<int:host_id>', methods=['DELETE'])
def api_delete_host(host_id):
    delete_host(host_id)
    return jsonify({'status': 'deleted'})
