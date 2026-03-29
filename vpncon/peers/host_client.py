from typing import Any
import requests
from dataclasses import dataclass

from .model import Peer
from vpncon.config import Config


class HostClientException(Exception):
    pass


@dataclass
class PeerForHost:
    peer_id: str
    peer_ip: str
    is_activated: bool

@dataclass
class PeerFromHost:
    peer_id: str
    peer_ip: str
    peer_private_key: str
    peer_public_key: str
    is_activated: bool

def build_peer_from_host(data: dict[str, Any]) -> PeerFromHost:
    return PeerFromHost(
        peer_id=data["peer_id"],
        peer_ip=data["peer_ip"],
        peer_private_key=data["peer_private_key"],
        peer_public_key=data["peer_public_key"],
        is_activated=data["is_activated"]
    )


class HostClient:
    def __init__(self, peer:Peer):
        self.peer_for_request = PeerForHost(
            peer_id=peer.conf_name,
            peer_ip=peer.peer_ip,
            is_activated=peer.is_active
        )

        self.host_url = (
            f"{Config.HOST_PROTOCOL}://{peer.host.ip_address}:{peer.host.port}/peers"
        )

        self.headers = {
            "Auth": peer.host.host_password
        }

    def _request(self, method: str, endpoint: str, json_body: dict[str, Any]|None=None):
        try:
            response = requests.request(
                method=method,
                url=f"{self.host_url}/{endpoint}",
                headers=self.headers,
                json=json_body,
                timeout=10,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            raise HostClientException(str(e)) from e

    def create_peer_on_host(self) -> PeerFromHost:
        endpoint = "peers"
        response = self._request(
            "POST",
            endpoint,
            json_body=self.peer_for_request.__dict__,
        )
        return build_peer_from_host(response.json()["peer"])

    def delete_peer_on_host(self):
        endpoint = f"peers/{self.peer_for_request.peer_id}"
        self._request("DELETE", endpoint)

    def get_peer_info(self) -> PeerFromHost:
        endpoint = f"peers/{self.peer_for_request.peer_id}"
        response = self._request("GET", endpoint)
        return build_peer_from_host(response.json()["peer"])

    def get_download_conf_token(self) -> str:
        endpoint = f"peers/{self.peer_for_request.peer_id}/download"
        response = self._request("GET", endpoint)
        return response.text

    def sync_peers_on_host(self):
        endpoint = f"peers/sync"
        self._request("POST", endpoint)

    def activate_on_host(self):
        endpoint = f"peers/{self.peer_for_request.peer_id}/activate"
        self._request("POST", endpoint)

    def deactivate_on_host(self):
        endpoint = f"peers/{self.peer_for_request.peer_id}/deactivate"
        self._request("POST", endpoint)
