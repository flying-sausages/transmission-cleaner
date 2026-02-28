"""Tests for orphaned file detection functionality."""

import pathlib
from unittest.mock import Mock, patch

import pytest

from transmission_cleaner.checkers.orphans import find_orphaned_files, get_tracked_files, scan_directory
from transmission_cleaner.main import handle_orphans


class TestScanDirectory:
    """Tests for directory scanning."""

    def test_scans_files_recursively(self, tmp_path):
        """Should scan all files in directory and subdirectories."""
        # Create test structure
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.txt").write_text("test")
        (tmp_path / "subdir" / "nested").mkdir()
        (tmp_path / "subdir" / "nested" / "file3.txt").write_text("test")

        result = scan_directory(tmp_path, include_hidden=False)

        assert len(result) == 3
        assert any(f.name == "file1.txt" for f in result)
        assert any(f.name == "file2.txt" for f in result)
        assert any(f.name == "file3.txt" for f in result)

    def test_excludes_hidden_files_by_default(self, tmp_path):
        """Should exclude hidden files unless explicitly included."""
        (tmp_path / "visible.txt").write_text("test")
        (tmp_path / ".hidden.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / ".hidden2.txt").write_text("test")

        result = scan_directory(tmp_path, include_hidden=False)

        assert len(result) == 1
        assert result[0].name == "visible.txt"

    def test_includes_hidden_files_when_requested(self, tmp_path):
        """Should include hidden files when flag is set."""
        (tmp_path / "visible.txt").write_text("test")
        (tmp_path / ".hidden.txt").write_text("test")

        result = scan_directory(tmp_path, include_hidden=True)

        assert len(result) == 2
        assert any(f.name == "visible.txt" for f in result)
        assert any(f.name == ".hidden.txt" for f in result)

    def test_excludes_system_and_torrent_files(self, tmp_path):
        """Should exclude system files and .torrent files."""
        (tmp_path / "file.txt").write_text("test")
        (tmp_path / ".DS_Store").write_text("test")
        (tmp_path / "movie.torrent").write_text("test")

        result = scan_directory(tmp_path, include_hidden=True)

        assert len(result) == 1
        assert result[0].name == "file.txt"

    def test_excludes_directories(self, tmp_path):
        """Should only return files, not directories."""
        (tmp_path / "file.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.txt").write_text("test")

        result = scan_directory(tmp_path, include_hidden=False)

        # Should have 2 files, not including the directory itself
        assert len(result) == 2
        assert all(f.is_file() for f in result)

    def test_excludes_symlinks(self, tmp_path):
        """Should exclude symlinks to prevent scanning outside directory."""
        # Create a real file inside the scan directory
        (tmp_path / "scan_dir").mkdir()
        (tmp_path / "scan_dir" / "real_file.txt").write_text("test")

        # Create a symlink file (should be excluded)
        symlink_file = tmp_path / "scan_dir" / "symlink.txt"
        symlink_file.symlink_to(tmp_path / "scan_dir" / "real_file.txt")

        # Create external directory outside scan_dir with files
        external = tmp_path / "external"
        external.mkdir()
        (external / "external_file.txt").write_text("test")

        # Create a symlink directory inside scan_dir pointing outside (should not be followed)
        external_symlink = tmp_path / "scan_dir" / "external_link"
        external_symlink.symlink_to(external)

        result = scan_directory(tmp_path / "scan_dir", include_hidden=False)

        # Should only have the real file, not the symlink file or files from symlinked directory
        assert len(result) == 1
        assert result[0].name == "real_file.txt"
        assert not any(f.is_symlink() for f in result)


class TestGetTrackedFiles:
    """Tests for getting tracked files from torrents."""

    def create_mock_torrent(self, torrent_id, download_dir, file_names):
        """Helper to create a mock torrent with files."""
        torrent = Mock()
        torrent.id = torrent_id
        torrent.download_dir = download_dir

        mock_files = []
        for file_name in file_names:
            mock_file = Mock()
            mock_file.name = file_name
            mock_files.append(mock_file)
        torrent.get_files.return_value = mock_files

        return torrent

    def test_collects_all_files_from_all_torrents(self):
        """Should collect all files from all torrents."""
        torrents = [
            self.create_mock_torrent(1, "/data", ["movie1.mkv", "subs1.srt"]),
            self.create_mock_torrent(2, "/data", ["movie2.mkv"]),
            self.create_mock_torrent(3, "/data", ["show.mkv", "subs2.srt"]),
        ]

        client = Mock()
        client.get_torrents.return_value = torrents

        result = get_tracked_files(client)

        assert len(result) == 5
        assert pathlib.Path("/data/movie1.mkv").resolve() in result
        assert pathlib.Path("/data/subs1.srt").resolve() in result
        assert pathlib.Path("/data/movie2.mkv").resolve() in result
        assert pathlib.Path("/data/show.mkv").resolve() in result
        assert pathlib.Path("/data/subs2.srt").resolve() in result

    def test_handles_no_torrents(self):
        """Should handle case with no torrents."""
        client = Mock()
        client.get_torrents.return_value = []

        result = get_tracked_files(client)

        assert result == set()

    def test_handles_different_download_dirs(self):
        """Should handle torrents with different download directories."""
        torrents = [
            self.create_mock_torrent(1, "/data/movies", ["movie.mkv"]),
            self.create_mock_torrent(2, "/data/tv", ["show.mkv"]),
        ]

        client = Mock()
        client.get_torrents.return_value = torrents

        result = get_tracked_files(client)

        assert len(result) == 2
        assert pathlib.Path("/data/movies/movie.mkv").resolve() in result
        assert pathlib.Path("/data/tv/show.mkv").resolve() in result


class TestFindOrphanedFiles:
    """Tests for finding orphaned files."""

    def test_identifies_orphaned_files(self, tmp_path):
        """Should identify files not in tracked set."""
        scanned = [
            tmp_path / "file1.txt",
            tmp_path / "file2.txt",
            tmp_path / "file3.txt",
        ]

        tracked = {
            (tmp_path / "file1.txt").resolve(),
            (tmp_path / "file2.txt").resolve(),
        }

        result = find_orphaned_files(scanned, tracked)

        assert len(result) == 1
        assert result[0].name == "file3.txt"

    def test_no_orphans_when_all_tracked(self, tmp_path):
        """Should return empty list when all files are tracked."""
        scanned = [
            tmp_path / "file1.txt",
            tmp_path / "file2.txt",
        ]

        tracked = {
            (tmp_path / "file1.txt").resolve(),
            (tmp_path / "file2.txt").resolve(),
        }

        result = find_orphaned_files(scanned, tracked)

        assert result == []

    def test_resolves_paths_for_comparison(self, tmp_path):
        """Should resolve paths to handle symlinks and relative paths."""
        # Create a real file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        scanned = [test_file]
        tracked = {test_file.resolve()}

        result = find_orphaned_files(scanned, tracked)

        # Should not be orphaned since resolved paths match
        assert result == []


class TestDirectoryValidation:
    """Tests for directory validation in handle_orphans.

    Tests the validation logic in handle_orphans() that ensures the specified
    directory is either the base download directory or a subdirectory within it.
    """

    def create_mock_client_and_args(self, base_dir, scan_dir, skip_disjoint=False):
        """Helper to create mocked client and args for testing."""
        # Mock client with session
        client = Mock()
        session = Mock()
        session.download_dir = str(base_dir)
        client.get_session.return_value = session
        client.get_torrents.return_value = []

        # Mock args
        args = Mock()
        args.directory = str(scan_dir)
        args.include_hidden = False
        args.action = "list"
        args.skip_disjoint = skip_disjoint

        return client, args

    @patch("transmission_cleaner.actions.process_orphaned_files", return_value=0)
    @patch("transmission_cleaner.checkers.orphans.find_orphaned_files", return_value=[])
    @patch("transmission_cleaner.checkers.orphans.get_tracked_files", return_value=set())
    @patch("transmission_cleaner.checkers.orphans.scan_directory", return_value=[])
    def test_directory_equals_base_path(self, mock_scan, mock_tracked, mock_find, mock_process, tmp_path):
        """Should allow directory that equals base download directory."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()

        client, args = self.create_mock_client_and_args(base_dir, base_dir)

        # Should complete without error
        handle_orphans(client, args)  # Should not raise

    @patch("transmission_cleaner.actions.process_orphaned_files", return_value=0)
    @patch("transmission_cleaner.checkers.orphans.find_orphaned_files", return_value=[])
    @patch("transmission_cleaner.checkers.orphans.get_tracked_files", return_value=set())
    @patch("transmission_cleaner.checkers.orphans.scan_directory", return_value=[])
    def test_directory_inside_base_path(self, mock_scan, mock_tracked, mock_find, mock_process, tmp_path):
        """Should allow subdirectory that is inside base download directory."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()
        subdir = base_dir / "movies"
        subdir.mkdir()

        client, args = self.create_mock_client_and_args(base_dir, subdir)

        # Should complete without error
        handle_orphans(client, args)  # Should not raise

    def test_directory_outside_base_path(self, tmp_path, capsys):
        """Directory that is outside base download directory should be rejected."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()
        other_dir = tmp_path / "other"
        other_dir.mkdir()

        client, args = self.create_mock_client_and_args(base_dir, other_dir)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            handle_orphans(client, args)
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "is not inside Transmission's base download directory" in captured.out

    def test_directory_is_parent_of_base_path(self, tmp_path, capsys):
        """Should reject directory that is a parent of base download directory."""
        base_dir = tmp_path / "downloads" / "torrents"
        base_dir.mkdir(parents=True)
        parent_dir = tmp_path / "downloads"

        client, args = self.create_mock_client_and_args(base_dir, parent_dir)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            handle_orphans(client, args)
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "is not inside Transmission's base download directory" in captured.out

    @patch("transmission_cleaner.actions.process_orphaned_files", return_value=0)
    @patch("transmission_cleaner.checkers.orphans.find_orphaned_files", return_value=[])
    @patch("transmission_cleaner.checkers.orphans.get_tracked_files", return_value=set())
    @patch("transmission_cleaner.checkers.orphans.scan_directory", return_value=[])
    def test_skip_disjoint_allows_any_directory(self, mock_scan, mock_tracked, mock_find, mock_process, tmp_path):
        """When skip_disjoint is True, directory validation should be bypassed."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()
        unrelated_dir = tmp_path / "completely_different"
        unrelated_dir.mkdir()

        # With skip_disjoint=True, should allow directory outside base
        client, args = self.create_mock_client_and_args(base_dir, unrelated_dir, skip_disjoint=True)

        # Should complete without error even though directory is outside base
        handle_orphans(client, args)  # Should not raise

    def test_nonexistent_directory_rejected(self, tmp_path, capsys):
        """Should reject a directory that doesn't exist."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()
        nonexistent = tmp_path / "does_not_exist"

        client, args = self.create_mock_client_and_args(base_dir, nonexistent)

        # Should exit with error before validation check
        with pytest.raises(SystemExit) as exc_info:
            handle_orphans(client, args)
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Directory not found" in captured.out

    def test_unresolved_directory_rejected(self, tmp_path, capsys):
        """Should reject a directory path that resolves outside the base download directory."""
        base_dir = tmp_path / "downloads"
        base_dir.mkdir()
        outside_base_dir = tmp_path / ".." / "does_not_exist"
        outside_base_dir.mkdir()

        client, args = self.create_mock_client_and_args(base_dir, outside_base_dir)

        # Should exit with error before validation check
        with pytest.raises(SystemExit) as exc_info:
            handle_orphans(client, args)
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "is not inside Transmission's base download directory" in captured.out
