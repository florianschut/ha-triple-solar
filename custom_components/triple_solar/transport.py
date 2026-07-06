"""Custom GQL transport for Triple Solar API with authentication and token refresh."""

import base64
import json
import logging
import time

from gql.transport.requests import RequestsHTTPTransport
import requests

_LOGGER = logging.getLogger(__name__)


class TripleSolarTransport(RequestsHTTPTransport):
    BASE_URL = "https://my.triplesolar.eu"
    auth_path = "/auth"
    graphql_path = "/graphql"
    access_token = None
    refresh_token = None
    claims = None

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self._init_super()

    def connect(self) -> None:
        """Connect to the API and obtain tokens if not already present."""
        if not self.access_token:
            _LOGGER.debug("Attempting to log in to Triple Solar API")
            try:
                resp = requests.post(
                    self._full_auth_path() + "/login",
                    json={"email": self.email, "password": self.password},
                    headers={
                        "Origin": self.BASE_URL,
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                )
                resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                _LOGGER.error("Error signing in to Triple Solar API: %s", e)
                raise Exception(f"Error signing in: {e}") from e

            data = resp.json()
            self.access_token = data.get("accessToken")
            self.refresh_token = data.get("refreshToken")
            if not self.access_token or not self.refresh_token:
                raise Exception("Access and refresh tokens not found in response")
            self.claims = self._claims_from_jwt(self.access_token)
            self._init_super()
            _LOGGER.debug("Successfully logged in and obtained tokens")
        super().connect()

    def execute(self, *args, **kwargs):
        """Execute a GraphQL query, refreshing token if necessary."""
        self._refresh_token()
        return super().execute(*args, **kwargs)

    def _refresh_token(self):
        """Refresh the access token if it's expired."""
        if not self._is_token_expired():
            return
        _LOGGER.debug("Access token expired, attempting to refresh")
        try:
            resp = requests.post(
                self._full_auth_path() + "/refresh",
                json={"refreshToken": self.refresh_token},
                headers={
                    "Origin": self.BASE_URL,
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + self.access_token,
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Error refreshing Triple Solar API token: %s", e)
            raise Exception(f"Error refreshing token: {e}") from e

        data = resp.json()
        self.access_token = data.get("accessToken")
        if not self.access_token:
            raise Exception("Access token not found in refresh response")
        self.claims = self._claims_from_jwt(self.access_token)
        super().close()
        self._init_super()
        super().connect()
        _LOGGER.debug("Successfully refreshed access token")

    def _full_auth_path(self):
        return self.BASE_URL + self.auth_path

    def _full_graphql_path(self):
        return self.BASE_URL + self.graphql_path

    @staticmethod
    def _claims_from_jwt(jwt):
        jwt_parts = jwt.split(".")
        if len(jwt_parts) != 3:
            raise Exception("Access token is not a JWT")
        claims_b64 = jwt_parts[1]
        missing_padding = len(claims_b64) % 4
        if missing_padding:
            claims_b64 += "=" * (4 - missing_padding)
        try:
            message_bytes = base64.b64decode(claims_b64.encode("ascii"))
            claims_str = message_bytes.decode("ascii")
            return json.loads(claims_str)
        except (base64.binascii.Error, json.JSONDecodeError) as e:
            raise Exception(f"Error decoding JWT claims: {e}") from e

    def _is_token_expired(self) -> bool:
        if not self.claims:
            return True
        exp_time = self.claims.get("exp")
        if not exp_time:
            _LOGGER.warning("JWT claims missing 'exp' field")
            return True
        return time.time() + 60 > exp_time

    def _init_super(self):
        headers = None
        if self.access_token:
            headers = {
                "Authorization": "Bearer " + self.access_token,
                "Origin": self.BASE_URL,
            }
        super().__init__(url=self._full_graphql_path(), headers=headers, verify=True)
