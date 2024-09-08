"""Tests for certbot_dns_cloudns._internal.authenticator."""

import sys
from unittest import mock

import pytest

from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

AUTH_ID = "1234"
SUB_AUTH_ID = "5678"
SUB_AUTH_USER = "tester"
AUTH_PASSWORD = "foobar"


class AuthenticatorTest(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    def setUp(self):
        from certbot_dns_cloudns._internal.authenticator import Authenticator

        super().setUp()

        path = os.path.join(self.tempdir, "file.ini")
        dns_test_common.write(
            {
                "cloudns_auth_id": AUTH_ID,
                "cloudns_auth_password": AUTH_PASSWORD,
            },
            path,
        )

        self.config = mock.MagicMock(
            cloudns_credentials=path,
            cloudns_propagation_seconds=0,  # don't wait during tests
            cloudns_nameserver="1.1.1.1",  # nameserver is required for parsing
        )
        self.auth = Authenticator(self.config, "cloudns")
        self.mock_client = mock.MagicMock()
        self.auth._get_client = mock.MagicMock(return_value=self.mock_client)

    @test_util.patch_display_util()
    def test_perform(self, unused_mock_get_utility):
        self.auth._change_txt_record = mock.MagicMock()
        self.auth._wait_for_change = mock.MagicMock()
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY, mock.ANY
            )
        ]
        assert expected == self.mock_client.mock_calls

    def test_cleanup(self):
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call.del_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
            )
        ]
        assert expected == self.mock_client.mock_calls

    @test_util.patch_display_util()
    def test_sub_auth_user(self, unused_mock_get_utility):
        dns_test_common.write(
            {
                "cloudns_sub_auth_user": SUB_AUTH_USER,
                "cloudns_auth_password": AUTH_PASSWORD,
            },
            self.config.cloudns_credentials,
        )
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY, mock.ANY
            )
        ]
        assert expected == self.mock_client.mock_calls

    @test_util.patch_display_util()
    def test_sub_auth_id(self, unused_mock_get_utility):
        dns_test_common.write(
            {
                "cloudns_sub_auth_id": SUB_AUTH_ID,
                "cloudns_auth_password": AUTH_PASSWORD,
            },
            self.config.cloudns_credentials,
        )
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY, mock.ANY
            )
        ]
        assert expected == self.mock_client.mock_calls

    def test_no_creds(self):
        dns_test_common.write({}, self.config.cloudns_credentials)
        with pytest.raises(errors.PluginError):
            self.auth.perform([self.achall])

    def test_missing_auth_password_or_auth_id(self):
        dns_test_common.write(
            {"cloudns_auth_id": AUTH_ID}, self.config.cloudns_credentials
        )
        with pytest.raises(errors.PluginError):
            self.auth.perform([self.achall])

        dns_test_common.write(
            {"clouds_auth_password": AUTH_PASSWORD},
            self.config.cloudns_credentials,
        )
        with pytest.raises(errors.PluginError):
            self.auth.perform([self.achall])


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv[1:] + [__file__]))  # pragma: no cover
