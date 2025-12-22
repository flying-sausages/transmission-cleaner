"""Tests for client configuration functionality."""

import json
from unittest.mock import mock_open, patch

from transmission_unlinked.client import create_client, get_client_config, load_settings_from_file


class TestLoadSettingsFromFile:
    """Tests for loading settings from file."""

    def test_load_settings(self):
        """Should load settings from JSON file."""
        settings_content = json.dumps({"rpc-port": 9091, "rpc-username": "user", "rpc-url": "/transmission/rpc"})

        with patch("builtins.open", mock_open(read_data=settings_content)):
            result = load_settings_from_file("settings.json", "pass")

        assert result["port"] == 9091
        assert result["username"] == "user"
        assert result["password"] == "pass"
        assert result["path"] == "/transmission/rpc"

    def test_load_settings_with_defaults(self):
        """Should use defaults for missing settings."""
        settings_content = json.dumps({})

        with patch("builtins.open", mock_open(read_data=settings_content)):
            result = load_settings_from_file("settings.json", "pass")

        assert result["port"] == 9091
        assert result["path"] == "/transmission/rpc"

    def test_load_settings_host_always_localhost(self):
        """Should always use 127.0.0.1 as host when loading from file."""
        settings_content = json.dumps({"rpc-port": 8080})

        with patch("builtins.open", mock_open(read_data=settings_content)):
            result = load_settings_from_file("settings.json", "pass")

        assert result["host"] == "127.0.0.1"


class TestGetClientConfig:
    """Tests for client configuration."""

    def test_config_from_args(self):
        """Should build config from command line args."""
        result = get_client_config(
            settings_file=None,
            protocol="https",
            host="192.168.1.1",
            port=8080,
            username="user",
            password="pass",
            path="/rpc",
        )

        assert result["protocol"] == "https"
        assert result["host"] == "192.168.1.1"
        assert result["port"] == 8080
        assert result["username"] == "user"
        assert result["password"] == "pass"
        assert result["path"] == "/rpc"

    def test_config_from_settings_file(self):
        """Should prefer settings file over args."""
        settings_content = json.dumps({"rpc-port": 9091})

        with patch("builtins.open", mock_open(read_data=settings_content)):
            result = get_client_config(
                settings_file="settings.json",
                password="pass",
            )

        assert result["port"] == 9091

    def test_config_defaults(self):
        """Should use default values when not specified."""
        result = get_client_config(password="pass")

        assert result["protocol"] == "http"
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 9091
        assert result["path"] == "/transmission/rpc"

    def test_config_without_password_no_settings_file(self):
        """Should handle missing password when no settings file."""
        result = get_client_config(settings_file=None, password=None)

        assert result["password"] is None

    def test_config_settings_file_requires_password(self):
        """Should not load settings file if password is None."""
        result = get_client_config(settings_file="settings.json", password=None)

        # Should fall back to manual config
        assert result["protocol"] == "http"
        assert result["password"] is None


class TestCreateClient:
    """Tests for client creation."""

    @patch("transmission_unlinked.client.Client")
    def test_create_client_with_config(self, mock_client_class):
        """Should create client with provided config."""
        config = {
            "host": "localhost",
            "port": 9091,
            "username": "user",
            "password": "pass",
        }

        create_client(**config)

        mock_client_class.assert_called_once_with(**config)

    @patch("transmission_unlinked.client.Client")
    def test_create_client_passes_all_params(self, mock_client_class):
        """Should pass all parameters to Client constructor."""
        config = {
            "protocol": "https",
            "host": "192.168.1.1",
            "port": 8080,
            "username": "admin",
            "password": "secret",
            "path": "/custom/rpc",
        }

        create_client(**config)

        mock_client_class.assert_called_once_with(**config)
