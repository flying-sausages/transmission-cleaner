from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for PTP.

    Args:
        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    PTP rules:
        Once you have downloaded at least 95% of a torrent, you must seed it for at least 48 hours within a 2 week period or until you have seeded at least one full copy (1:1).
    """
    if torrent.ratio >= 1 or torrent.percent_complete < 0.95:
        return True
    return torrent.seconds_seeding >= 48 * 3600
