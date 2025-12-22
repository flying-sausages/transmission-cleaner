"""Tests for main module functionality."""

from unittest.mock import patch

import pytest

from transmission_unlinked.main import parse_args


class TestParseArgs:
    """Tests for argument parsing."""

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass"])
    def test_minimal_args_with_defaults(self):
        """Should parse with just password and use default values."""
        args = parse_args()

        assert args.password == "pass"
        assert args.host == "127.0.0.1"
        assert args.port == 9091
        assert args.min_days == 7
        assert args.action is None
        assert args.directory is None
        assert args.tracker is None

    @patch(
        "sys.argv",
        [
            "transmission-unlinked",
            "--password",
            "pass",
            "--dir",
            "/data/movies",
            "--tracker",
            "tracker.com",
            "--min-days",
            "30",
            "--action",
            "list",
            "--host",
            "192.168.1.100",
            "--port",
            "8080",
        ],
    )
    def test_all_arguments_parsed_correctly(self):
        """Should correctly parse all arguments when provided."""
        args = parse_args()

        assert args.password == "pass"
        assert args.directory == "/data/movies"
        assert args.tracker == "tracker.com"
        assert args.min_days == 30
        assert args.action == "list"
        assert args.host == "192.168.1.100"
        assert args.port == 8080

    @patch("sys.argv", ["transmission-unlinked"])
    def test_missing_required_password(self):
        """Should require password argument."""
        with pytest.raises(SystemExit):
            parse_args()

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "invalid"])
    def test_invalid_action_rejected(self):
        """Should reject invalid action choices."""
        with pytest.raises(SystemExit):
            parse_args()

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--settings-file", "/path/to/settings.json"])
    def test_settings_file_option(self):
        """Should parse settings file path for alternate config."""
        args = parse_args()

        assert args.settings_file == "/path/to/settings.json"
