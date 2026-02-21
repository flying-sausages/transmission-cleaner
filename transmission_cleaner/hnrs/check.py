from typing import Callable

from transmission_rpc.torrent import Torrent

import transmission_cleaner.hnrs as hnrs

hnr_map: dict[str, Callable] = {
    "landof.tv": hnrs.btn.is_outside_hnr,
    "tracker.beyond-hd.me": hnrs.bhd.is_outside_hnr,
    "please.passthepopcorn.me": hnrs.ptp.is_outside_hnr,
    "tvchaos.uk": hnrs.tvcuk.is_outside_hnr,
}


def check_hnr(torrent: Torrent) -> list[str]:
    """Checks against known HNR rules for private trackers. Returns False if no matching tracker is found, or a list of violating trackers."""
    violations: list[str] = []
    for tracker in torrent.trackers:
        if tracker.announce in hnr_map:
            hnr_check = hnr_map[tracker.announce]
            if not hnr_check(torrent):
                violations.append(tracker.announce)
        else:
            print(f"[WARN] Torrent markes as private but '{tracker.announce}' HNR rules not known. Make a simple PR ")
    return violations
