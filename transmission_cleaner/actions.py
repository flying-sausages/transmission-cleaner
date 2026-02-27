"""Torrent and file action processing functionality."""

import pathlib
from collections.abc import Mapping, Sequence

from transmission_rpc import Client, Torrent

from transmission_cleaner.hnrs.check import CheckHnrResult, get_hnrs


def process_torrents(
    client: Client,
    torrents: Sequence[Torrent],
    action: str | None,
    cross_seed_map: Mapping[int, Sequence[Torrent]] | None = None,
    check_hnrs: bool = True,
) -> int:
    """Process torrents based on the specified action.

    Args:
        client: Transmission RPC client
        torrents: List of torrents to process
        action: Action to perform - None (interactive), "list"/"l", "delete"/"d", "remove"/"r"
        cross_seed_map: Optional dict mapping torrent IDs to list of cross-seeding torrents.
                       If provided, protects cross-seeded torrents from data deletion.
        check_hnrs: Whether to check HNR status for private torrents before performing actions.

    Returns:
        Total bytes freed (only counts data that was actually deleted)
    """
    cross_seed_map = cross_seed_map or {}
    total_space_freed = 0

    # Handle action based on argument
    if action in ["list", "l"]:
        removable_bits = 0
        for torrent in torrents:
            ret = get_hnrs(torrent) if torrent.is_private and check_hnrs else CheckHnrResult.empty()
            hnr = f" [HNR violations: {', '.join(ret.violations)}]" if ret.violations else ""
            cross_status = " [CROSS-SEEDED]" if torrent.id in cross_seed_map else ""
            size_gb = torrent.total_size / (1024**3)
            print(f"  - {torrent.name}{cross_status}{hnr} ({size_gb:.2f} GB)")
            if warns := ret.get_unknown_str():
                print("    ^ " + warns)

            if not check_hnrs or not torrent.is_private or not ret.violations:
                # Only count size towards removable total if it doesn't have HNR violations
                removable_bits += torrent.total_size
        print(
            f"\nSize of all torrents that could be removed (duplicates not accounted for): {removable_bits / (1024**3):.2f} GB"
        )
    elif action in ["delete", "d", "remove", "r"]:
        for torrent in torrents:
            # If deleting something cross-seeded, only remove torrent
            if action in ["d", "delete"] and torrent.id in cross_seed_map:
                # Cross-seeded: protect data, remove torrent only
                print(f"[PROTECTED] {torrent.name}: Cross-seeded, removing torrent only (keeping data)")
                client.remove_torrent(torrent.id, delete_data=False)
                continue

            # Skip deletion if private torrent has HNR violations, otherwise proceed with specified action
            ret = get_hnrs(torrent) if torrent.is_private and check_hnrs else CheckHnrResult.empty()
            if torrent.is_private and check_hnrs and ret.violations:
                # Private torrent with HNR violations: protect torrent and data, skipping deletion to keep seeding
                print(f"[PROTECTED] {torrent.name}: HNR violations ({', '.join(ret.violations)}), skipping")
                continue

            # Safe to perform action
            if action in ["d", "delete"]:
                size_gb = torrent.total_size / (1024**3)
                print(f"[ACTION] {torrent.name}: Removing with data ({size_gb:.2f} GB)")
                client.remove_torrent(torrent.id, delete_data=True)
                total_space_freed += torrent.total_size
            else:
                print(f"[ACTION] {torrent.name}: Removing without data")
                client.remove_torrent(torrent.id, delete_data=False)

            if warns := ret.get_unknown_str():
                print("^  " + warns)

    elif action in ["interactive", "i", None]:
        # Interactive mode
        for torrent in torrents:
            print()
            cross_status = " [CROSS-SEEDED]" if torrent.id in cross_seed_map else ""
            ret = get_hnrs(torrent) if torrent.is_private and check_hnrs else CheckHnrResult.empty()
            hnr = f" [HNR violations: {', '.join(ret.violations)}]" if ret.violations else ""
            if warns := ret.get_unknown_str():
                print(warns)
            choice = (
                input(f"[PROMPT] {torrent.name}{cross_status}{hnr}\n         Remove torrent? [N(o)/r(emove)/d(ata)] ")
                .strip()
                .lower()
                or "n"
            )

            if choice == "r":
                if ret.violations:
                    # Private torrent with HNR violations: keep torrent seeding
                    print(f"[PROTECTED] {torrent.name}: HNR violations ({', '.join(ret.violations)}), keeping torrent")
                    continue
                print(f"[ACTION] {torrent.name}: Removing without data")
                client.remove_torrent(torrent.id, delete_data=False)
            elif choice == "d":
                if ret.violations:
                    # Private torrent with HNR violations: keep torrent seeding, do not delete data
                    print(
                        f"[PROTECTED] {torrent.name}: HNR violations ({', '.join(ret.violations)}), keeping torrent and data"
                    )
                    continue
                elif torrent.id in cross_seed_map:
                    # Cross-seeded: protect data even if user wants to delete
                    print(f"[PROTECTED] {torrent.name}: Cross-seeded, removing torrent only (keeping data)")
                    client.remove_torrent(torrent.id, delete_data=False)
                else:
                    # Not cross-seeded: safe to delete data
                    size_gb = torrent.total_size / (1024**3)
                    print(f"[ACTION] {torrent.name}: Removing with data ({size_gb:.2f} GB)")
                    client.remove_torrent(torrent.id, delete_data=True)
                    total_space_freed += torrent.total_size
            else:
                print("[SKIP]   Skipped")

    return total_space_freed


def process_orphaned_files(
    orphaned_files: Sequence[pathlib.Path],
    action: str | None,
) -> int:
    """Process orphaned files based on the specified action.

    Args:
        orphaned_files: List of orphaned file paths to process
        action: Action to perform - None (interactive), "list"/"l", "delete"/"d"

    Returns:
        Total bytes freed (only counts files that were actually deleted)
    """
    total_space_freed = 0

    if action in ["list", "l"]:
        for file_path in sorted(orphaned_files):
            try:
                size = file_path.stat().st_size if file_path.exists() else 0
                size_mb = size / (1024 * 1024)
                print(f"  - {file_path} ({size_mb:.2f} MB)")
            except (OSError, PermissionError) as e:
                print(f"  - {file_path} [ERROR: {e}]")

    elif action in ["delete", "d"]:
        for file_path in orphaned_files:
            try:
                if file_path.exists():
                    size = file_path.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"[ACTION] Deleting: {file_path} ({size_mb:.2f} MB)")
                    file_path.unlink()
                    total_space_freed += size
                else:
                    print(f"[SKIP]   File no longer exists: {file_path}")
            except (OSError, PermissionError) as e:
                print(f"[ERROR]  Failed to delete {file_path}: {e}")

    else:  # interactive mode
        for file_path in orphaned_files:
            try:
                if not file_path.exists():
                    print(f"[SKIP]   File no longer exists: {file_path}")
                    continue
                size = file_path.stat().st_size
                size_mb = size / (1024 * 1024)
                choice = input(f"[PROMPT] {file_path} ({size_mb:.2f} MB)\n         Delete file? [y/N] ").strip().lower()
                if choice == "y":
                    print(f"[ACTION] Deleting: {file_path}")
                    file_path.unlink()
                    total_space_freed += size
                else:
                    print("[SKIP]   Skipped")
            except (OSError, PermissionError) as e:
                print(f"[ERROR]  Cannot process {file_path}: {e}")

    return total_space_freed
