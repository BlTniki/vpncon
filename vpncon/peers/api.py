from typing import Any
from flask import jsonify, request
from vpncon.db import auto_transaction
from .model import Peer
from . import peers_bp, peer_service
from ..users.model import User
from ..hosts.model import Host

def user_to_dict(user: User) -> dict[str, Any]:
    return {
        'telegram_id': user.telegram_id,
        'telegram_nick': user.telegram_nick,
        'role': user.role.value
    }

def host_to_dict(host: Host) -> dict[str, Any]:
    return {
        'id': host.id,
        'name': host.name,
        'ip_address': host.ip_address,
        'port': host.port,
        'host_password': host.host_password
    }

def to_dict(peer: Peer) -> dict[str, Any]:
    return {
        'user': user_to_dict(peer.user),
        'host': host_to_dict(peer.host),
        'conf_name': peer.conf_name,
        'peer_ip': peer.peer_ip,
        'is_active': peer.is_active
    }


@peers_bp.route('/<int:telegram_id>', methods=['GET'])
@auto_transaction()
def api_get_user_peers(telegram_id: int):
    conf_name = request.args.get('conf_name')
    if not conf_name:
        peers = peer_service.get_all_peers_by_user(telegram_id)
    else:
        peer = peer_service.get_peer(telegram_id, conf_name)
        peers = [peer] if peer else []

    if peers:
        return jsonify([to_dict(peer) for peer in peers])
    return jsonify({'error': 'Peers not found'}), 404


@peers_bp.route('/', methods=['POST'])
@auto_transaction()
def api_create_user_subscription():
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    peer_service.create_peer(
        data.get('telegram_id'), data.get('host_id'), data.get('conf_name')
    )
    return jsonify({'status': 'created'}), 201


@peers_bp.route('/switch_active', methods=['PUT'])
@auto_transaction()
def api_switch_peer_active():
    data = request.json
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    peer_service.switch_peer_active_status(
        data.get('telegram_id'), data.get('conf_name'), data.get('is_active')
    )
    return jsonify({'status': 'updated'})


@peers_bp.route('/<int:telegram_id>', methods=['DELETE'])
@auto_transaction()
def api_delete_peer(telegram_id: int):
    conf_name = request.args.get('conf_name')
    if not conf_name:
        return jsonify({'error': 'URL QUERY `conf_name` required'}), 400
    peer_service.delete_peer(telegram_id, conf_name)
    return jsonify({'status': 'deleted'})


@peers_bp.route('/<int:telegram_id>/download_token', methods=['GET'])
@auto_transaction()
def api_get_peer_download_token(telegram_id: int):
    conf_name = request.args.get('conf_name')
    if not conf_name:
        return jsonify({'error': 'URL QUERY `conf_name` required'}), 400

    return jsonify({'token': f'{peer_service.get_peer_download_token(telegram_id, conf_name)}'})
