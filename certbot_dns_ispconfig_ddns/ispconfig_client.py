"""DNS Authenticator for ISPConfig."""
import logging

import requests

# prevent urllib3 to log request with the api token
logging.getLogger("urllib3").setLevel(logging.WARNING)

TXT_MAX_LEN = 255
DDNS_SCRIPT_PATH = "/ddns/update.php"


class ISPConfigClientError(Exception):
    """
    Errors directly from ISPConfigClient.
    """
    pass


class ISPConfigClient:
    """
    Encapsulates all communication with the ISPConfig Remote REST API.
    """

    def __init__(self, endpoint: str, token: str) -> None:
        """
        Creates a new ISPConfigClient object.

        :param token: the ISPConfig DDNS module token used for API calls
        :raise ISPConfigClientError: if the endpoint or token are missing
        """
        if endpoint is None or len(endpoint) == 0:
            raise ISPConfigClientError(f"Missing endpoint: {endpoint}")
        if token is None or len(token) == 0:
            raise ISPConfigClientError(f"Missing token: {token}")
        self._endpoint = endpoint.rstrip("/")
        self._token = token.strip()

    def set_txt_record(self, record_fqdn: str, record_content: str) -> None:
        """
        Add a TXT record using the supplied information.

        :param str record_fqdn: the validation record including domain name
                                (typically beginning with '_acme-challenge.')
        :param str record_content: The record TXT content that should be set
        :raises ISPConfigClientError: if an error occurs
        """
        if len(record_content) > TXT_MAX_LEN:
            raise ISPConfigClientError(
                f"TXT record is too big, max {TXT_MAX_LEN} chars allowed"
            )
        update_url = f"{self._endpoint}{DDNS_SCRIPT_PATH}"
        query_params = {
            "action": "add",
            "type": "TXT",
            "record": record_fqdn,
            "data": record_content,
        }
        response: requests.Response = requests.post(
            url=update_url,
            params=query_params,
            auth=('anonymous', self._token)
        )
        response.raise_for_status()

    def del_txt_record(self, record_fqdn: str, record_content: str) -> None:
        """
        Delete a TXT record using the supplied information.

        :param str record_fqdn: the validation record including domain name
                                (typically beginning with '_acme-challenge.')
        :param str record_content: The record TXT content that should be set
        :raises ISPConfigClientError: if an error occurs
        """
        if len(record_content) > TXT_MAX_LEN:
            raise ISPConfigClientError(
                f"TXT record is too big, max {TXT_MAX_LEN} chars allowed"
            )
        update_url = f"{self._endpoint}{DDNS_SCRIPT_PATH}"
        query_params = {
            "action": "delete",
            "type": "TXT",
            "record": record_fqdn,
            "data": record_content,
        }
        response: requests.Response = requests.delete(
            url=update_url,
            params=query_params,
            auth=('anonymous', self._token)
        )
        response.raise_for_status()
