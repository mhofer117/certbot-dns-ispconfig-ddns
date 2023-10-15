"""Tests for certbot_dns_ispconfig.dns_ispconfig."""
import unittest

import mock
from certbot import errors
from certbot._internal.display import obj as display_obj
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_ispconfig_ddns.authenticator import Authenticator

TEST_ENDPOINT = "http://endpoint"
TEST_TOKEN = "token123"


class AuthenticatorTest(
    test_util.TempDirTestCase,
    dns_test_common.BaseAuthenticatorTest,
    unittest.TestCase,
):

    def setUp(self):
        # manually mock ISPConfigClient class
        patcher = mock.patch(
            'certbot_dns_ispconfig_ddns.authenticator.ISPConfigClient'
        )
        self.addCleanup(patcher.stop)
        self.mock_client = patcher.start()

        super(AuthenticatorTest, self).setUp()
        display_obj.set_display(mock.Mock())

        self._create_authenticator_with_credentials_file()

    def _create_authenticator_with_credentials_file(self):
        path = os.path.join(self.tempdir, "file.ini")
        dns_test_common.write(
            {
                "ispconfig_ddns_endpoint": TEST_ENDPOINT,
                "ispconfig_ddns_token": TEST_TOKEN,
            },
            path
        )

        self.config = mock.MagicMock(
            ispconfig_ddns_credentials=path,
            ispconfig_ddns_propagation_seconds=0,  # don't wait during tests
            ispconfig_ddns_endpoint=None,
            ispconfig_ddns_token=None,
        )
        self.auth = Authenticator(self.config, "ispconfig_ddns")
        self.auth._setup_credentials()

    def _create_authenticator_with_cli_params(self):
        self.config = mock.MagicMock(
            ispconfig_ddns_propagation_seconds=0,  # don't wait during tests
            ispconfig_ddns_endpoint=TEST_ENDPOINT,
            ispconfig_ddns_token=TEST_TOKEN,
        )
        self.auth = Authenticator(self.config, "ispconfig_ddns")

    def test_setup_credentials(self):
        self.auth._configure_file = mock.MagicMock()
        self.auth._configure_credentials = mock.MagicMock()
        self.auth._setup_credentials()

        self.assertEqual(
            [mock.call('credentials', 'ISPConfig DDNS credentials INI file')],
            self.auth._configure_file.mock_calls
        )
        self.assertEqual(
            [mock.call('credentials', 'ISPConfig DDNS credentials INI file', {
                "endpoint": "URL of the ISPConfig Installation.",
                "token": "The generated DDNS module token.",
            })],
            self.auth._configure_credentials.mock_calls
        )

        self._create_authenticator_with_cli_params()
        self.auth._configure_file = mock.MagicMock()
        self.auth._configure_credentials = mock.MagicMock()
        self.auth._setup_credentials()

        self.assertEqual([], self.auth._configure_file.mock_calls)
        self.assertEqual([], self.auth._configure_credentials.mock_calls)

    def test_get_ispconfig_client_credentials_file(self):
        client = self.auth._get_ispconfig_client()

        expected = [
            mock.call(endpoint=TEST_ENDPOINT, token=TEST_TOKEN)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)
        assert client is self.mock_client.return_value

    def test_get_ispconfig_client_cli_params(self):
        self._create_authenticator_with_cli_params()
        client = self.auth._get_ispconfig_client()

        expected = [
            mock.call(endpoint=TEST_ENDPOINT, token=TEST_TOKEN)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)
        assert client is self.mock_client.return_value

    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [
            mock.call(endpoint=TEST_ENDPOINT, token=TEST_TOKEN),
            mock.call().set_txt_record("_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_perform_with_exception(self):
        ex = KeyError('foo')
        self.mock_client().set_txt_record = mock.Mock(
            side_effect=ex
        )
        with self.assertRaises(errors.PluginError) as err:
            self.auth.perform([self.achall])

        self.assertEqual(err.exception.args[0], ex)

    def test_cleanup(self):
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call(endpoint=TEST_ENDPOINT, token=TEST_TOKEN),
            mock.call().del_txt_record("_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup_with_exception(self):
        self.auth._attempt_cleanup = True
        ex = KeyError('bar')
        self.mock_client().del_txt_record = mock.Mock(
            side_effect=ex
        )
        with self.assertRaises(errors.PluginError) as err:
            self.auth.cleanup([self.achall])

        self.assertEqual(err.exception.args[0], ex)


if __name__ == "__main__":
    unittest.main()
