"""Tests for main module functionality."""

from unittest.mock import patch

import pytest

from transmission_unlinked.main import parse_args


class TestParseArgs:
    """Tests for argument parsing."""

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass"])
    def test_minimal_args(self):
        """Should parse with just password."""
        args = parse_args()

        assert args.password == "pass"
        assert args.host == "127.0.0.1"
        assert args.port == 9091
        assert args.min_days == 7
        assert args.action is None

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--dir", "/data/movies"])
    def test_with_directory_filter(self):
        """Should parse directory filter argument."""
        args = parse_args()

        assert args.directory == "/data/movies"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--tracker", "tracker.example.com"])
    def test_with_tracker_filter(self):
        """Should parse tracker filter argument."""
        args = parse_args()

        assert args.tracker == "tracker.example.com"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--min-days", "14"])
    def test_with_min_days(self):
        """Should parse min-days argument."""
        args = parse_args()

        assert args.min_days == 14

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "list"])
    def test_with_list_action(self):
        """Should parse list action."""
        args = parse_args()

        assert args.action == "list"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "delete"])
    def test_with_delete_action(self):
        """Should parse delete action."""
        args = parse_args()

        assert args.action == "delete"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "d"])
    def test_with_delete_action_short(self):
        """Should parse delete action short form."""
        args = parse_args()

        assert args.action == "d"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "remove"])
    def test_with_remove_action(self):
        """Should parse remove action."""
        args = parse_args()

        assert args.action == "remove"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--settings-file", "/path/to/settings.json"])
    def test_with_settings_file(self):
        """Should parse settings file argument."""
        args = parse_args()

        assert args.settings_file == "/path/to/settings.json"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--protocol", "https"])
    def test_with_https_protocol(self):
        """Should parse protocol argument."""
        args = parse_args()

        assert args.protocol == "https"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--host", "192.168.1.100"])
    def test_with_custom_host(self):
        """Should parse custom host."""
        args = parse_args()

        assert args.host == "192.168.1.100"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--port", "8080"])
    def test_with_custom_port(self):
        """Should parse custom port."""
        args = parse_args()

        assert args.port == 8080

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--username", "admin"])
    def test_with_username(self):
        """Should parse username."""
        args = parse_args()

        assert args.username == "admin"

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--path", "/custom/rpc"])
    def test_with_custom_path(self):
        """Should parse custom RPC path."""
        args = parse_args()

        assert args.path == "/custom/rpc"

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
        ],
    )
    def test_with_all_filters(self):
        """Should parse multiple filter arguments together."""
        args = parse_args()

        assert args.directory == "/data/movies"
        assert args.tracker == "tracker.com"
        assert args.min_days == 30
        assert args.action == "list"

    @patch("sys.argv", ["transmission-unlinked"])
    def test_missing_password(self):
        """Should require password."""
        with pytest.raises(SystemExit):
            parse_args()

    @patch("sys.argv", ["transmission-unlinked", "--password", "pass", "--action", "invalid"])
    def test_invalid_action(self):
        """Should reject invalid action."""
        with pytest.raises(SystemExit):
            parse_args()
