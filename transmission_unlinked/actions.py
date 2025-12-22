"""Torrent action processing functionality."""

from transmission_rpc import Client, Torrent


def process_torrents(
    client: Client,
    torrents: list[Torrent],
    action: str | None,
    cross_seed_map: dict[int, list[Torrent]] | None = None,
):
    """Process torrents based on the specified action.

    Args:
        client: Transmission RPC client
        torrents: List of torrents to process
        action: Action to perform - None (interactive), "list"/"l", "delete"/"d", "remove"/"r"
        cross_seed_map: Optional dict mapping torrent IDs to list of cross-seeding torrents.
                       If provided, protects cross-seeded torrents from data deletion.
    """
    cross_seed_map = cross_seed_map or {}

    # Handle action based on argument
    if action in ["list", "l"]:
        for torrent in torrents:
            cross_status = " [CROSS-SEEDED]" if torrent.id in cross_seed_map else ""
            print(f"  - {torrent.name}{cross_status}")

    elif action in ["delete", "d"]:
        for torrent in torrents:
            if torrent.id in cross_seed_map:
                # Cross-seeded: protect data, remove torrent only
                print(f"[PROTECTED] {torrent.name}: Cross-seeded, removing torrent only (keeping data)")
                client.remove_torrent(torrent.id, delete_data=False)
            else:
                # Not cross-seeded: safe to delete data
                print(f"[ACTION] {torrent.name}: Removing with data")
                client.remove_torrent(torrent.id, delete_data=True)

    elif action in ["remove", "r"]:
        for torrent in torrents:
            print(f"[ACTION] {torrent.name}: Removing without data")
            client.remove_torrent(torrent.id, delete_data=False)

    elif action in ["interactive", "i", None]:
        # Interactive mode
        for torrent in torrents:
            cross_status = " [CROSS-SEEDED]" if torrent.id in cross_seed_map else ""
            choice = (
                input(f"[PROMPT] {torrent.name}{cross_status}\n         Remove torrent? [N(o)/r(emove)/d(ata)] ")
                .strip()
                .lower()
                or "n"
            )

            if choice == "r":
                print(f"[ACTION] {torrent.name}: Removing without data")
                client.remove_torrent(torrent.id, delete_data=False)
            elif choice == "d":
                if torrent.id in cross_seed_map:
                    # Cross-seeded: protect data even if user wants to delete
                    print(f"[PROTECTED] {torrent.name}: Cross-seeded, removing torrent only (keeping data)")
                    client.remove_torrent(torrent.id, delete_data=False)
                else:
                    # Not cross-seeded: safe to delete data
                    print(f"[ACTION] {torrent.name}: Removing with data")
                    client.remove_torrent(torrent.id, delete_data=True)
            else:
                print("[SKIP]   Skipped")
