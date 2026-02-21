from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for BTN.

    Args:
        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    BTN HNR criteria:
    1) Seed all individual episodes for 24 hours or until you reach a 1:1 ratio.
    2) Seed all season packs for 120 hours or until you reach a 1:1 ratio.
    3) You must meet the minimum seed time OR ratio requirements within 2 weeks of starting the download.
    """
    # Any torrent
    if torrent.ratio >= 1:
        return True
    # Single episodes require 24hrs seed
    if torrent.file_count == 1:
        return torrent.seconds_seeding >= 24 * 3600
    # Seasons require 120hrs
    else:
        return torrent.seconds_seeding >= 120 * 3600
