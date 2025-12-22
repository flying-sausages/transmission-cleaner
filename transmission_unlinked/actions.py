"""Torrent action processing functionality."""

from transmission_rpc import Client, Torrent


def process_torrents(client: Client, torrents: list[Torrent], action: str | None):
    """Process torrents based on the specified action.

    Args:
        client: Transmission RPC client
        torrents: List of torrents to process
        action: Action to perform - None (interactive), "list"/"l", "delete"/"d", "remove"/"r"
    """
    # Handle action based on argument
    if action in ["list", "l"]:
        for torrent in torrents:
            print(f"  - {torrent.name}")
    elif action in ["delete", "d"]:
        for torrent in torrents:
            print(f"[ACTION] {torrent.name}: Removing with data")
            client.remove_torrent(torrent.id, delete_data=True)
    elif action in ["remove", "r"]:
        for torrent in torrents:
            print(f"[ACTION] {torrent.name}: Removing without data")
            client.remove_torrent(torrent.id, delete_data=False)
    else:
        # Interactive mode
        for torrent in torrents:
            choice = input(f"[PROMPT] {torrent.name}\n         Remove torrent? [N/y/d(ata)] ").strip().lower() or "n"
            if choice == "y":
                print(f"[ACTION] {torrent.name}: Removing without data")
                client.remove_torrent(torrent.id, delete_data=False)
            elif choice == "d":
                print(f"[ACTION] {torrent.name}: Removing with data")
                client.remove_torrent(torrent.id, delete_data=True)
            else:
                print("[SKIP]   Skipped")
