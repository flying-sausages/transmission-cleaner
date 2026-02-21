from unittest.mock import Mock

from transmission_cleaner.hnrs.btn import is_outside_hnr


def test_is_outside_hnr():
    mock_torrent = Mock()
    mock_torrent.ratio = 1.5

    assert is_outside_hnr(mock_torrent)


def test_is_outside_hnr_single_episode():
    mock_torrent = Mock()
    mock_torrent.ratio = 0.5
    mock_torrent.file_count = 1
    mock_torrent.seconds_seeding = 23 * 3600

    assert not is_outside_hnr(mock_torrent)

    mock_torrent.seconds_seeding = 24 * 3600
    assert is_outside_hnr(mock_torrent)


def test_is_outside_hnr_season_pack():
    mock_torrent = Mock()
    mock_torrent.ratio = 0.5
    mock_torrent.file_count = 10
    mock_torrent.seconds_seeding = 119 * 3600

    assert not is_outside_hnr(mock_torrent)

    mock_torrent.seconds_seeding = 120 * 3600
    assert is_outside_hnr(mock_torrent)
