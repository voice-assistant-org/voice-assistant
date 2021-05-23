"""HTTP interface helper functions."""

import socket


def get_my_ip() -> str:
    """Get localhost IP address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]  # type: ignore
