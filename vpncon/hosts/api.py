from typing import Any
from flask import jsonify, request
from vpncon.db import auto_transaction
from .model import Host
from ..hosts import hosts_bp, host_service

def to_dict(host: Host) -> dict[str, Any]:
    return {
            'id': host.id,
            'name': host.name,
            'ip_address': host.ip_address,
            'port': host.port,
            'password': host.host_password
        }

@hosts_bp.route('/<int:host_id>', methods=['GET'])
@auto_transaction()
def api_get_host(host_id: int):
    host = host_service.get_host(host_id)
    if host:
        return jsonify(to_dict(host))
    return jsonify({'error': 'Host not found'}), 404


@hosts_bp.route('/', methods=['POST'])
@auto_transaction()
def api_create_host():
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    host_service.create_host(
        data.get('id'), data.get('name'), data.get('ip_address'), data.get('port'), data.get('password')
    )
    return jsonify({'status': 'created'}), 201


@hosts_bp.route('/<int:host_id>', methods=['PUT'])
@auto_transaction()
def api_update_host(host_id: int):
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    host_service.update_host(
        host_id, data.get('name'), data.get('ip_address'), data.get('port'), data.get('password')
    )
    return jsonify({'status': 'updated'})


@hosts_bp.route('/<int:host_id>', methods=['DELETE'])
@auto_transaction()
def api_delete_host(host_id: int):
    host_service.delete_host(host_id)
    return jsonify({'status': 'deleted'})
