from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for PTP.

    Args:        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    BHD rules:
    - All torrents MUST be seeded for 120 hours (5 days) OR a ratio of 1:1. Seeding only begins after you finish downloading 100% of the torrent. If you fail to seed a completed download for 48 continuous hours you will get a pre warning. After this pre warning, if you fail to seed it within 3 days you will accumulate a HNR. If you accumulate 3 HNR's your account will lose download rights. Your account will only get those rights restored after you have seeded off the HNR(s). You may redownload the .torrent files and the data (if buffer permits).
    - If you download less than 30% of a torrent, and stop the torrent then a HNR will not be accumulated.
    - If you download 30% or more of a torrent, you must complete 100% of the torrent and seed as normal to avoid an HNR.
    """
    if torrent.ratio >= 1:
        return True
    if torrent.percent_done < 0.30:
        return True
    return torrent.seconds_seeding >= 120 * 3600
