"""Tests for action processing functionality."""

from unittest.mock import Mock, patch

from transmission_cleaner.actions import process_torrents


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

    @patch("builtins.print")
    def test_delete_action_removes_with_data(self, mock_print):
        """Delete action should remove torrents and their data."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "d")

        client.remove_torrent.assert_called_with(1, delete_data=True)

    @patch("builtins.print")
    def test_remove_action_keeps_data(self, mock_print):
        """Remove action should remove torrents but keep data."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "r")

        client.remove_torrent.assert_called_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_remove(self, mock_input, mock_print):
        """Interactive mode should remove without data when user chooses 'r'."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "r"

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_called_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_delete(self, mock_input, mock_print):
        """Interactive mode should remove with data when user chooses 'd'."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "d"

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_called_with(1, delete_data=True)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_skip(self, mock_input, mock_print):
        """Interactive mode should skip when user chooses 'n' or empty."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "n"

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

    @patch("builtins.print")
    def test_delete_action_protects_cross_seeded_torrents(self, mock_print):
        """Delete action should keep data for cross-seeded torrents."""
        client = Mock()
        torrents = [
            self.create_mock_torrent("t1", 1),
            self.create_mock_torrent("t2", 2),
        ]
        cross_seed_map = {1: [Mock()]}  # t1 is cross-seeded

        process_torrents(client, torrents, "delete", cross_seed_map)

        # t1 should be removed without deleting data (protected)
        client.remove_torrent.assert_any_call(1, delete_data=False)
        # t2 should be removed with data (not cross-seeded)
        client.remove_torrent.assert_any_call(2, delete_data=True)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_protects_cross_seeded_on_delete(self, mock_input, mock_print):
        """Interactive mode should protect cross-seeded torrents even if user chooses delete."""
        client = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        cross_seed_map = {1: [Mock()]}  # t1 is cross-seeded

        # User chooses 'd' (delete with data)
        mock_input.return_value = "d"
        process_torrents(client, torrents, None, cross_seed_map)

        # Should remove without data due to cross-seed protection
        client.remove_torrent.assert_called_with(1, delete_data=False)
