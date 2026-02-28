from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for BHD.

    Args:
        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    BHD rules:
    - All torrents MUST be seeded for 120 hours (5 days) OR a ratio of 1:1. Seeding only begins after you finish downloading 100% of the torrent.
    - If you download less than 30% of a torrent, and stop the torrent then a HNR will not be accumulated.
    - If you download 30% or more of a torrent, you must complete 100% of the torrent and seed as normal to avoid an HNR.
    """
    if torrent.ratio >= 1:
        return True
    if torrent.percent_complete < 0.30:
        return True
    if torrent.percent_complete < 1:
        return False
    return torrent.seconds_seeding >= 120 * 3600
