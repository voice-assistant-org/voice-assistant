"""HTTP interface subpackage."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable

from flask import Flask

from voiceassistant.const import PORT
from voiceassistant.utils.log import get_logger
from voiceassistant.utils.network import get_my_ip

from .api_app import api_factory

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


_LOGGER = get_logger(__name__)

# disable flask message
cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None  # type: ignore


class HttpInterface:
    """HTTP interface."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize flask app."""
        self._vass = vass
        self._host = get_my_ip()
        self.app = Flask(__name__)
        self.register_factories(api_factory)

    @property
    def url(self) -> str:
        """Get api url."""
        return f"http://{self._host}:{PORT}"

    def register_factories(self, *factories: Callable) -> None:
        """Register Flask app factories."""
        for factory in factories:
            self.app = factory(vass=self._vass, app=self.app)

    def run(self) -> None:
        """Run app."""
        _LOGGER.info(f"Starting webserver at: {self.url}")
        try:
            self.app.run(self._host, port=PORT)
        except OSError as e:
            _LOGGER.error(f"Failed to start webserver. {e}")
