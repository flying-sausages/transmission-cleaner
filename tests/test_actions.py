"""Tests for action processing functionality."""

from unittest.mock import Mock, patch

import pytest
from transmission_rpc import Torrent, Tracker

from transmission_cleaner.actions import process_torrents


def create_mock_torrent(name, torrent_id, total_size=1024**3):
    """Helper to create a mock torrent."""
    torrent = Mock(spec=Torrent)
    torrent.name = name
    torrent.id = torrent_id
    torrent.total_size = total_size  # Default to 1 GB
    torrent.is_private = False
    return torrent


def create_mock_torrent_private(*args, **kwargs):
    torrent = create_mock_torrent("t1", 1)
    torrent.is_private = True
    torrent.ratio = 0.67
    torrent.seconds_seeding = 123123
    tracker = Mock(spec=Tracker)
    tracker.announce = "https://landof.tv:3232/asdasdasdasdasd"
    torrent.trackers = [tracker]
    return torrent


class TestProcessTorrents:
    """Tests for torrent processing actions."""

    @patch("builtins.print")
    def test_list_action_does_not_remove(self, mock_print):
        """List action should display torrents without removing them."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]

        result = process_torrents(client, torrents, "list")

        assert result == 0  # List action doesn't free space

        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_delete_action_removes_with_data(self, mock_print):
        """Delete action should remove torrents and their data."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]

        result = process_torrents(client, torrents, "d")

        client.remove_torrent.assert_called_with(1, delete_data=True)
        assert result == 1024**3  # Should return 1 GB

    @patch("builtins.print")
    def test_remove_action_keeps_data(self, mock_print):
        """Remove action should remove torrents but keep data."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]

        result = process_torrents(client, torrents, "r")

        client.remove_torrent.assert_called_with(1, delete_data=False)
        assert result == 0  # Remove without data doesn't free space
        assert result == 0  # Remove action doesn't delete data

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_remove(self, mock_input, mock_print):
        """Interactive mode should remove without data when user chooses 'r'."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]
        mock_input.return_value = "r"

        _ = process_torrents(client, torrents, "interactive")

        client.remove_torrent.assert_called_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_delete(self, mock_input, mock_print):
        """Interactive mode should remove with data when user chooses 'd'."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]
        mock_input.return_value = "d"

        result = process_torrents(client, torrents, "interactive")

        client.remove_torrent.assert_called_with(1, delete_data=True)
        assert result == 1024**3  # Should return 1 GB

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_skip(self, mock_input, mock_print):
        """Interactive mode should skip when user chooses 'n' or empty."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]
        mock_input.return_value = "n"

        result = process_torrents(client, torrents, "interactive")

        client.remove_torrent.assert_not_called()
        assert result == 0  # Skip doesn't free space

    @patch("builtins.print")
    def test_processes_multiple_torrents(self, mock_print):
        """Should process all torrents in the list."""
        client = Mock()
        torrents = [
            create_mock_torrent("t1", 1),
            create_mock_torrent("t2", 2),
            create_mock_torrent("t3", 3),
        ]

        result = process_torrents(client, torrents, "r")

        assert client.remove_torrent.call_count == 3
        client.remove_torrent.assert_any_call(1, delete_data=False)
        client.remove_torrent.assert_any_call(2, delete_data=False)
        client.remove_torrent.assert_any_call(3, delete_data=False)
        assert result == 0  # Remove action doesn't delete data

    @patch("builtins.print")
    def test_delete_action_protects_cross_seeded_torrents(self, mock_print):
        """Delete action should keep data for cross-seeded torrents."""
        client = Mock()
        torrents = [
            create_mock_torrent("t1", 1),
            create_mock_torrent("t2", 2),
        ]
        cross_seed_map = {1: [Mock(spec=Torrent)]}  # t1 is cross-seeded

        result = process_torrents(client, torrents, "delete", cross_seed_map)

        # t1 should be removed without deleting data (protected)
        client.remove_torrent.assert_any_call(1, delete_data=False)
        # t2 should be removed with data (not cross-seeded)
        client.remove_torrent.assert_any_call(2, delete_data=True)
        assert result == 1024**3  # Only t2 was deleted with data (1 GB)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_protects_cross_seeded_on_delete(self, mock_input, mock_print):
        """Interactive mode should protect cross-seeded torrents even if user chooses delete."""
        client = Mock()
        torrents = [create_mock_torrent("t1", 1)]
        cross_seed_map = {1: [Mock(spec=Torrent)]}  # t1 is cross-seeded

        # User chooses 'd' (delete with data)
        mock_input.return_value = "d"
        result = process_torrents(client, torrents, "interactive", cross_seed_map)

        # Should remove without data due to cross-seed protection
        client.remove_torrent.assert_called_with(1, delete_data=False)
        assert result == 0  # Cross-seeded torrent was protected


class TestProcessTorrentsWithHnr:
    @patch("builtins.print")
    @patch("builtins.input")
    @pytest.mark.parametrize("response", ["r", "d"])
    def test_protects_hnr_interactive(self, mock_input, mock_print, response):
        """Interactive mode should protect torrents with HNR violations even if user chooses remove."""
        client = Mock()
        torrent = create_mock_torrent_private()
        cross_seed_map = {}

        result = process_torrents(client, [torrent], "r", cross_seed_map, True)

        mock_input.return_value = response
        result = process_torrents(client, [torrent], "interactive", cross_seed_map, check_hnrs=True)
        client.remove_torrent.assert_not_called()
        assert result == 0  # Torrent with HNR violations was protected

    @patch("builtins.print")
    @pytest.mark.parametrize("response", ["r", "d"])
    def test_protects_hnr_direct(self, mock_print, response):
        """Direct mode should protect torrents with HNR violations even if user chooses remove."""
        client = Mock()
        torrent = create_mock_torrent_private()
        cross_seed_map = {}

        result = process_torrents(client, [torrent], response, cross_seed_map, check_hnrs=True)
        client.remove_torrent.assert_not_called()
        assert result == 0  # Torrent with HNR violations was protected

    @patch("builtins.print")
    @patch("builtins.input")
    @pytest.mark.parametrize("response", ["r", "d"])
    def test_deletes_hnr_interactive(self, mock_input, mock_print, response):
        """Interactive mode should delete torrents without HNRs"""
        client = Mock()
        torrent = create_mock_torrent_private()
        torrent.ratio = 120

        mock_input.return_value = response
        result = process_torrents(client, [torrent], "interactive", cross_seed_map={}, check_hnrs=True)
        client.remove_torrent.assert_called()
        if response == "r":
            assert result == 0
        else:
            assert result == 1024**3  # Should return 1 GB for delete action

    @patch("builtins.print")
    @pytest.mark.parametrize("response", ["r", "d"])
    def test_deletes_hnr_direct(self, mock_print, response):
        """Direct mode should delete torrents without HNRs"""
        torrent = create_mock_torrent_private()
        torrent.ratio = 120

        client = Mock()
        result = process_torrents(client, [torrent], response, cross_seed_map={}, check_hnrs=True)
        client.remove_torrent.assert_called()
        if response == "r":
            assert result == 0
        else:
            assert result == 1024**3  # Should return 1 GB for delete action
