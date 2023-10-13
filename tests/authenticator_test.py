"""Tests for certbot_dns_ispconfig.dns_ispconfig."""
import unittest

import mock
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
        super(AuthenticatorTest, self).setUp()
        display_obj.set_display(mock.Mock())
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
            ispconfig_ddns_propagation_seconds=0  # don't wait during tests
        )
        self.auth = Authenticator(self.config, "ispconfig_ddns")
        self.mock_client = mock.MagicMock()
        # _get_ispconfig_client | pylint: disable=protected-access
        self.auth._get_ispconfig_client = mock.MagicMock(
            return_value=self.mock_client
        )

    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [
            mock.call.set_txt_record(
                "_acme-challenge." + DOMAIN, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call.del_txt_record(
                "_acme-challenge." + DOMAIN, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)


if __name__ == "__main__":
    unittest.main()
