"""Tests for action processing functionality."""

from unittest.mock import Mock, patch

from transmission_unlinked.actions import process_torrents


class TestProcessTorrents:
    """Tests for torrent processing actions."""

    def create_mock_torrent(self, name, torrent_id):
        """Helper to create a mock torrent."""
        torrent = Mock()
        torrent.name = name
        torrent.id = torrent_id
        return torrent

    @patch("builtins.print")
    def test_list_action_does_not_remove(self, mock_print):
        """List action should display torrents without removing them."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "list")

        client.remove_torrent.assert_not_called()

        # Also test short form
        process_torrents(client, torrents, "l")
        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_delete_action_removes_with_data(self, mock_print):
        """Delete action should remove torrents and their data."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "delete")

        client.remove_torrent.assert_called_with(1, delete_data=True)

        # Also test short form
        client.reset_mock()
        process_torrents(client, torrents, "d")
        client.remove_torrent.assert_called_with(1, delete_data=True)

    @patch("builtins.print")
    def test_remove_action_keeps_data(self, mock_print):
        """Remove action should remove torrents but keep data."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "remove")

        client.remove_torrent.assert_called_with(1, delete_data=False)

        # Also test short form
        client.reset_mock()
        process_torrents(client, torrents, "r")
        client.remove_torrent.assert_called_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_respects_user_choice(self, mock_input, mock_print):
        """Interactive mode should handle different user inputs correctly."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        # Test 'y' - remove without data
        mock_input.return_value = "y"
        process_torrents(client, torrents, None)
        client.remove_torrent.assert_called_with(1, delete_data=False)

        # Test 'd' - remove with data
        client.reset_mock()
        mock_input.return_value = "d"
        process_torrents(client, torrents, None)
        client.remove_torrent.assert_called_with(1, delete_data=True)

        # Test 'n' or empty - skip
        client.reset_mock()
        mock_input.return_value = "n"
        process_torrents(client, torrents, None)
        client.remove_torrent.assert_not_called()

        client.reset_mock()
        mock_input.return_value = ""
        process_torrents(client, torrents, None)
        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_processes_multiple_torrents(self, mock_print):
        """Should process all torrents in the list."""
        client = Mock()
        torrents = [
            self.create_mock_torrent("t1", 1),
            self.create_mock_torrent("t2", 2),
            self.create_mock_torrent("t3", 3),
        ]

        process_torrents(client, torrents, "r")

        assert client.remove_torrent.call_count == 3
        client.remove_torrent.assert_any_call(1, delete_data=False)
        client.remove_torrent.assert_any_call(2, delete_data=False)
        client.remove_torrent.assert_any_call(3, delete_data=False)
