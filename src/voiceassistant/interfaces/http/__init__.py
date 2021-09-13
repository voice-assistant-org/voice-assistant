"""HTTP interface subpackage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from flask import Flask

from .api_app import api_factory
from .helpers import get_my_ip

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

PORT = 5050


class HttpInterface:
    """HTTP interface."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize flask app."""
        self._vass = vass

        self.app = Flask(__name__)
        self.register_factories(api_factory)

    def register_factories(self, *factories: Callable) -> None:
        """Register Flask app factories."""
        for factory in factories:
            self.app = factory(vass=self._vass, app=self.app)

    def run(self) -> None:
        """Run app."""
        self.app.run(get_my_ip(), port=PORT)
