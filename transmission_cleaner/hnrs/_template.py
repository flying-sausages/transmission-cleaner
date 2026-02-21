from transmission_rpc import Torrent


def is_outside_hnr(torrent: Torrent) -> bool:
    """Determine if a torrent is outside of HNR criteria for WEBSITE_XYZ.

    Args:        torrent: The torrent to check

    Returns:
        False if deleting would incur HNR, True if it's safe to delete without HNR risk

    WEBSITE_XYZ rules:
        ... # Paste rules from site here
    """
    ...  # Implement here
