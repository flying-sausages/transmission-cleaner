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
class CheckHnrResult:
    violations: list[str]
    """List of announce addresses for which a HNR would be incurred if the torrent were removed."""
    unknowns: list[str]
    """List of announce addresses for which no HNR rules are known, and thus no check was performed."""

    def get_unknown_str(self) -> str:
        if self.unknowns:
            return f"[WARN] HNR rules unknown for trackers: {', '.join(self.unknowns)}, please make a PR ;)"
        return ""

    @classmethod
    def empty(cls):
        return cls([], [])


def get_hnrs(torrent: Torrent) -> CheckHnrResult:
    """Checks against known HNR rules for private trackers."""
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
    return CheckHnrResult(violations, unknowns)
