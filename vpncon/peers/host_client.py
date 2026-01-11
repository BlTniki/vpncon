from typing import Any
import requests
from dataclasses import dataclass

from .model import Peer


class HostClientException(Exception):
    pass


@dataclass
class PeerForHost:
    peerId: str
    peerIp: str

@dataclass
class PeerFromHost:
    peerId: str
    peerIp: str
    peerPrivateKey: str
    peerPublicKey: str

def build_peer_from_host(data: dict[str, Any]) -> PeerFromHost:
    return PeerFromHost(
        peerId=data["peerId"],
        peerIp=data["peerIp"],
        peerPrivateKey=data["peerPrivateKey"],
        peerPublicKey=data["peerPublicKey"],
    )


class HostClient:
    api_version = "1.0"

    def __init__(self, peer:Peer):
        self.peer_for_request = PeerForHost(
            peerId=f"{peer.conf_name}",
            peerIp=peer.peer_ip,
        )

        self.host_ip_address = (
            f"http://{peer.host.ip_address}:{peer.host.port}/api/{self.api_version}"
        )

        self.headers = {
            "Auth": peer.host.host_password
        }

    def _request(self, method: str, url: str, json_body: dict[str, Any]|None=None):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_body,
                timeout=10,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            raise HostClientException(str(e)) from e

    def create_peer_on_host(self) -> PeerFromHost:
        url = f"{self.host_ip_address}/peers"
        response = self._request(
            "POST",
            url,
            json_body=self.peer_for_request.__dict__,
        )
        return build_peer_from_host(response.json())

    def delete_peer_on_host(self):
        url = f"{self.host_ip_address}/peers/{self.peer_for_request.peerId}"
        self._request("DELETE", url)

    def get_download_conf_token(self) -> str:
        url = f"{self.host_ip_address}/conf/{self.peer_for_request.peerId}"
        response = self._request("POST", url)
        return response.text

    def activate_on_host(self):
        url = f"{self.host_ip_address}/peers/activate/{self.peer_for_request.peerId}"
        self._request("POST", url)

    def deactivate_on_host(self):
        url = f"{self.host_ip_address}/peers/deactivate/{self.peer_for_request.peerId}"
        self._request("POST", url)
