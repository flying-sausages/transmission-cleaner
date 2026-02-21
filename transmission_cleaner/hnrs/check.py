from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from transmission_rpc import Torrent

import transmission_cleaner.hnrs as hnrs

hnr_map: dict[str, Callable] = {
    "landof.tv": hnrs.btn.is_outside_hnr,
    "tracker.beyond-hd.me": hnrs.bhd.is_outside_hnr,
    "please.passthepopcorn.me": hnrs.ptp.is_outside_hnr,
    "tvchaosuk.com": hnrs.tvcuk.is_outside_hnr,
}


@dataclass
class CheckHNRResult:
    violations: list[str]
    unknowns: list[str]

    def __bool__(self) -> bool:
        return bool(self.violations) or bool(self.unknowns)

    def get_unknowns(self) -> str:
        if self.unknowns:
            return f"  [INFO] No HNR rules for trackers: {', '.join(self.unknowns)}"
        return ""


def check_hnr(torrent: Torrent) -> CheckHNRResult:
    """Checks against known HNR rules for private trackers. Returns a list of violating trackers; returns an empty list if no matching tracker is found or no violations occur."""
    violations: list[str] = []
    unknowns: list[str] = []
    for tracker in torrent.trackers:
        domain = str(urlparse(tracker.announce).hostname)
        if domain in hnr_map:
            hnr_check = hnr_map[domain]
            if not hnr_check(torrent):
                violations.append(domain)
        else:
            unknowns.append(domain)
    return CheckHNRResult(violations, unknowns)
