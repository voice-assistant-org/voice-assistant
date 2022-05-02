"""Network related util functions."""

import socket
import uuid


def get_my_ip() -> str:
    """Get IP-address of the host device."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]  # type: ignore


def get_uuid() -> str:
    """Get UUID of the host device."""
    return str(uuid.getnode())


def get_mac() -> str:
    """Get MAC-address of the host device."""
    mac = "%012x" % uuid.getnode()
    return ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))
