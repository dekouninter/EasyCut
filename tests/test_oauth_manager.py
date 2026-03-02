# -*- coding: utf-8 -*-
"""Tests for oauth_manager.py — OAuth authentication without network."""

import json
import pytest
from unittest.mock import MagicMock, patch
from oauth_manager import OAuthManager, OAuthError


class TestOAuthError:
    def test_is_exception(self):
        assert issubclass(OAuthError, Exception)

    def test_can_raise_and_catch(self):
        with pytest.raises(OAuthError, match="test error"):
            raise OAuthError("test error")

    def test_message_preserved(self):
        err = OAuthError("detailed message")
        assert str(err) == "detailed message"


class TestOAuthManagerInit:
    def test_init_creates_paths(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        assert om.config_dir.exists()

    def test_scopes_readonly(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        assert "youtube.readonly" in om.SCOPES[0]

    def test_not_authenticated_initially(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        assert om.is_authenticated() is False


class TestOAuthManagerLoadCredentials:
    def test_load_from_file(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        creds = om._load_credentials()
        assert "installed" in creds
        assert creds["installed"]["client_id"] == "test-client-id.apps.googleusercontent.com"

    def test_load_from_init_data(self, tmp_config):
        creds_data = {
            "installed": {
                "client_id": "from-init.apps.googleusercontent.com",
                "client_secret": "init-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        }
        om = OAuthManager(config_dir=str(tmp_config), credentials_data=creds_data)
        loaded = om._load_credentials()
        assert loaded["installed"]["client_id"] == "from-init.apps.googleusercontent.com"

    def test_load_no_credentials_raises(self, tmp_config):
        om = OAuthManager(config_dir=str(tmp_config))
        with pytest.raises(OAuthError):
            om._load_credentials()

    def test_load_corrupt_credentials_raises(self, tmp_config):
        (tmp_config / "credentials.json").write_text("invalid json {{{")
        om = OAuthManager(config_dir=str(tmp_config))
        with pytest.raises(OAuthError):
            om._load_credentials()


class TestOAuthManagerTokenFile:
    def test_save_and_load_token(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        # Mock credentials object with necessary attributes
        mock_creds = MagicMock()
        mock_creds.token = "test-token"
        mock_creds.refresh_token = "test-refresh"
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "test-client-id"
        mock_creds.client_secret = "test-client-secret"
        mock_creds.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        om.creds = mock_creds
        result = om._save_token()
        assert result is True
        assert om.token_file.exists()

    def test_load_token_no_file(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        result = om._load_token()
        assert result is False

    def test_load_corrupt_token(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        om.token_file.write_text("not valid json")
        result = om._load_token()
        assert result is False


class TestOAuthManagerLogout:
    def test_logout_no_files(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        result = om.logout()
        assert result is True

    def test_logout_clears_creds(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        om.creds = MagicMock()
        result = om.logout()
        assert result is True
        assert om.creds is None

    def test_logout_deletes_token_file(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        om.token_file.write_text("{}")
        om.logout()
        assert not om.token_file.exists()


class TestOAuthManagerDeleteToken:
    def test_delete_token_when_exists(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        om.token_file.write_text("{}")
        om.delete_token()
        assert not om.token_file.exists()

    def test_delete_token_when_not_exists(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        # Should not raise
        om.delete_token()


class TestOAuthManagerGetUserEmail:
    def test_no_creds_returns_none(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        assert om.get_user_email() is None

    def test_with_mock_creds(self, tmp_config_with_creds):
        om = OAuthManager(config_dir=str(tmp_config_with_creds))
        mock_creds = MagicMock()
        mock_creds.token = "test-token"
        om.creds = mock_creds
        # Without network, this will fail gracefully
        result = om.get_user_email()
        # Either None or a string (depends on whether Google API is mocked)
        assert result is None or isinstance(result, str)
