import os
from typing import Optional

import requests


def _approle_login(url: str, approle_name: str, approle_secret: str) -> Optional[str]:
    data = {
        "role_id": approle_name,
        "secret_id": approle_secret,
    }
    response = requests.post(url, data=data)
    try:
        return response.json()["data"]["token"]
    except KeyError:
        return None


class Vault:
    def __init__(self, addr=None, token=None, approle_name=None, approle_secret=None, path=None):
        if not addr:
            addr = os.getenv("VAULT_ADDR")
        if not addr:
            raise ValueError("No VAULT_ADDR given")
        self.addr = addr

        if not token:
            token = os.getenv("VAULT_TOKEN", token)

        if not token and (not approle_name and not approle_secret):
            raise ValueError("You need to specify either token or approle login data")

        if approle_name and approle_secret:
            self._token = _approle_login(self.addr, approle_name, approle_secret)
        else:
            self._token = token

        self.path = path

    def _get_url(self, path: str) -> str:
        return f"{self.addr}/v1/{path}"

    def read_secret(self) -> str:
        headers = {
            "X-Vault-Token": f"{self._token}"
        }
        url = self._get_url(self.path)
        response = requests.get(url, headers=headers)
        return response.json()["data"]["data"]["token"]
