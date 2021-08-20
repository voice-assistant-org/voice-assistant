"""Add-On functions for triggerword detection event."""

import os
import random
import subprocess
from functools import lru_cache

from voiceassistant.config import Config
from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR
from voiceassistant.exceptions import ConfigValidationError
from voiceassistant.interfaces.base import InterfaceIO


def _react_by_random_phrase(interface: InterfaceIO) -> None:
    """React to trigger word by a random reply phrase."""
    interface.output(
        text=random.choice(Config.triggerword.replies), cache=True,
    )


def _react_by_sound(interface: InterfaceIO) -> None:
    """React to trigger detection word."""
    subprocess.Popen(["mpg123", _get_soundfile_path(Config.triggerword.sound)])


@lru_cache()
def _get_soundfile_path(name: str) -> str:
    """Get triggerword reaction sound path."""
    path_preset = f"{DATA_DIR}/audio/{name}.mp3"
    path_custom = f"{DEFAULT_CONFIG_DIR}/audio/{name}.mp3"

    if os.path.isfile(path_preset):
        return path_preset
    elif os.path.isfile(path_custom):
        return path_custom
    else:
        raise ConfigValidationError(f"sound file '{name}' doesn't exist")


def _do_not_react(interface: InterfaceIO) -> None:
    """Do nothing if reaction is not set in Config."""
    print("Keyword detected")


if "sound" in Config.triggerword:
    react_to_keyword = _react_by_sound
elif "replies" in Config.triggerword:
    react_to_keyword = _react_by_random_phrase
else:
    react_to_keyword = _do_not_react
