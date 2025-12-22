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
    def test_list_action(self, mock_print):
        """List action should not remove torrents."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "list")

        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_list_action_short_form(self, mock_print):
        """List action 'l' should not remove torrents."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "l")

        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_delete_action(self, mock_print):
        """Delete action should remove with data."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "d")

        client.remove_torrent.assert_called_once_with(1, delete_data=True)

    @patch("builtins.print")
    def test_delete_action_long_form(self, mock_print):
        """Delete action 'delete' should remove with data."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "delete")

        client.remove_torrent.assert_called_once_with(1, delete_data=True)

    @patch("builtins.print")
    def test_remove_action(self, mock_print):
        """Remove action should remove without data."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "r")

        client.remove_torrent.assert_called_once_with(1, delete_data=False)

    @patch("builtins.print")
    def test_remove_action_long_form(self, mock_print):
        """Remove action 'remove' should remove without data."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]

        process_torrents(client, torrents, "remove")

        client.remove_torrent.assert_called_once_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_yes(self, mock_input, mock_print):
        """Interactive mode should remove without data when user says yes."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "y"

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_called_once_with(1, delete_data=False)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_delete(self, mock_input, mock_print):
        """Interactive mode should remove with data when user says delete."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "d"

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_called_once_with(1, delete_data=True)

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_skip(self, mock_input, mock_print):
        """Interactive mode should skip when user says no."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = "n"

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    @patch("builtins.input")
    def test_interactive_mode_empty_input(self, mock_input, mock_print):
        """Interactive mode should skip on empty input (default to no)."""
        client = Mock()
        client.remove_torrent = Mock()
        torrents = [self.create_mock_torrent("t1", 1)]
        mock_input.return_value = ""

        process_torrents(client, torrents, None)

        client.remove_torrent.assert_not_called()

    @patch("builtins.print")
    def test_multiple_torrents(self, mock_print):
        """Should process multiple torrents."""
        client = Mock()
        client.remove_torrent = Mock()
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
