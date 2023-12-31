"""Tests for certbot_dns_ispconfig.dns_ispconfig."""
import unittest

import requests
import responses
from certbot.plugins.dns_test_common import DOMAIN

from certbot_dns_ispconfig_ddns.ispconfig_client import ISPConfigClient, \
    ISPConfigClientError

TEST_ENDPOINT = "http://endpoint"
TEST_TOKEN = "token123"


class ISPConfigClientTest(unittest.TestCase):
    record_fqdn = DOMAIN
    record_content = "bar"

    def setUp(self):
        self.client = ISPConfigClient(TEST_ENDPOINT, TEST_TOKEN)

    def test_missing_endpoint(self):
        with self.assertRaises(ISPConfigClientError) as err:
            ISPConfigClient('', TEST_TOKEN)
        self.assertEqual(err.exception.args[0], "Missing endpoint: ")

    def test_missing_token(self):
        with self.assertRaises(ISPConfigClientError) as err:
            ISPConfigClient(TEST_ENDPOINT, '')
        self.assertEqual(err.exception.args[0], "Missing token: ")

    def test_set_txt_record_too_big(self):
        with self.assertRaises(ISPConfigClientError) as err:
            self.client.set_txt_record(DOMAIN, 'a' * 256)
        self.assertEqual(
            err.exception.args[0],
            "TXT record is too big, max 255 chars allowed"
        )

    @responses.activate
    def test_set_txt_record_not_found(self):
        responses.add(**{
            'method': responses.POST,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=add&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'NOP',
            'status': 404,
        })
        with self.assertRaises(requests.exceptions.HTTPError) as err:
            self.client.set_txt_record(DOMAIN, self.record_content)
        self.assertEqual(err.exception.response.status_code, 404)

    @responses.activate
    def test_set_txt_record_permission_denied(self):
        responses.add(**{
            'method': responses.POST,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=add&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'NOP',
            'status': 401,
        })
        with self.assertRaises(requests.exceptions.HTTPError) as err:
            self.client.set_txt_record(DOMAIN, self.record_content)
        self.assertEqual(err.exception.response.status_code, 401)

    @responses.activate
    def test_set_txt_record(self):
        responses.add(**{
            'method': responses.POST,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=add&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'OK',
            'status': 200,
        })
        self.client.set_txt_record(DOMAIN, self.record_content)

    def test_del_txt_record_too_big(self):
        with self.assertRaises(ISPConfigClientError) as err:
            self.client.del_txt_record(DOMAIN, 'a' * 256)
        self.assertEqual(
            err.exception.args[0],
            "TXT record is too big, max 255 chars allowed"
        )

    @responses.activate
    def test_del_txt_record_not_found(self):
        responses.add(**{
            'method': responses.DELETE,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=delete&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'NOP',
            'status': 404,
        })
        with self.assertRaises(requests.exceptions.HTTPError) as err:
            self.client.del_txt_record(DOMAIN, self.record_content)
        self.assertEqual(err.exception.response.status_code, 404)

    @responses.activate
    def test_del_txt_record_permission_denied(self):
        responses.add(**{
            'method': responses.DELETE,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=delete&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'NOP',
            'status': 401,
        })
        with self.assertRaises(requests.exceptions.HTTPError) as err:
            self.client.del_txt_record(DOMAIN, self.record_content)
        self.assertEqual(err.exception.response.status_code, 401)

    @responses.activate
    def test_del_txt_record(self):
        responses.add(**{
            'method': responses.DELETE,
            'url': (f"{TEST_ENDPOINT}/ddns/update.php?action=delete&type=TXT&"
                    f"record={DOMAIN}&data={self.record_content}"),
            'body': 'OK',
            'status': 200,
        })
        self.client.del_txt_record(DOMAIN, self.record_content)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
