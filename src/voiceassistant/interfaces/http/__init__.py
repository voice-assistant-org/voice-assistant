"""HTTP interface subpackage."""

from typing import Callable

from flask import Flask

from .api_app import api_factory
from .helpers import get_my_ip

PORT = 5050


class HttpInterface:
    """HTTP interface."""

    def __init__(self, vass) -> None:  # type: ignore
        """Initialize flask app."""
        self.vass = vass

        self.app = Flask(__name__)
        self.register_factories(api_factory)

    def register_factories(self, *factories: Callable) -> None:
        """Register Flask app factories."""
        for factory in factories:
            self.app = factory(vass=self.vass, app=self.app)

    def run(self) -> None:
        """Run app."""
        self.app.run(get_my_ip(), port=PORT)
