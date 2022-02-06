"""Handle HTTP server authentication."""

import secrets
import string
from functools import wraps
from typing import Any, Callable

import flask
from flask import request

from voiceassistant.const import DEFAULT_CONFIG_DIR
from voiceassistant.utils.log import get_logger

_LOGGER = get_logger(__name__)


def _get_token() -> str:
    """Create if needed and return API token."""
    tokenfile = f"{DEFAULT_CONFIG_DIR}/API_TOKEN"

    try:
        with open(tokenfile) as file:
            return file.read()
    except FileNotFoundError:
        token = _generate_token()

        print(f"\n\nPlease save auto-generated API token: {token}\n\n")

        with open(tokenfile, "w") as file:
            file.write(token)

        return token


def _generate_token(n_chars: int = 50) -> str:
    """Generate API token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(n_chars))


TOKEN = _get_token()


def authorized(func: Callable) -> Callable:
    """Wrap Flask handler function to check for auth TOKEN."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if TOKEN == request.headers.get("token"):
            return func(*args, **kwargs)
        else:
            _LOGGER.warning(f"Unauthorized API request in {func.__name__}")
            return flask.Response("<b>401: Unauthorized</b>", status=401)

    return wrapper
