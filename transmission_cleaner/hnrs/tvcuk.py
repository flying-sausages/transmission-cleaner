from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for TVCUK.

    Args:
        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    TVCUK rules:
        * You should aim to seed single episode torrents for a minimum of 24 hours and 72 hours for full packs
    """

    if torrent.file_count == 1:
        return torrent.seconds_seeding >= 24 * 3600
    else:
        return torrent.seconds_seeding >= 72 * 3600
