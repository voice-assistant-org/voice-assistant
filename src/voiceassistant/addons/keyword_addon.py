"""Add-On functions for triggerword detection event."""

from __future__ import annotations

import os
import random
import subprocess
from functools import lru_cache
from typing import TYPE_CHECKING

from voiceassistant.config import Config
from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR
from voiceassistant.exceptions import ConfigValidationError
from voiceassistant.utils.log import get_logger

from .create import CoreAttribute, addon_end

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _do_not_react(vass: VoiceAssistant) -> None:
    """Do nothing if reaction is not set in Config."""
    _LOGGER.info("Keyword detected")


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _react_by_random_phrase(vass: VoiceAssistant) -> None:
    """React to trigger word by a random reply phrase."""
    _LOGGER.info("Keyword detected")
    vass.interfaces.speech.output(text=random.choice(Config.triggerword.replies), cache=True)


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _react_by_sound(vass: VoiceAssistant) -> None:
    """React to trigger detection word."""
    _LOGGER.info("Keyword detected")
    subprocess.Popen(
        ["mpg123", _get_soundfile_path(Config.triggerword.sound)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


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


if "sound" in Config.triggerword:
    react_to_keyword = _react_by_sound
elif "replies" in Config.triggerword:
    react_to_keyword = _react_by_random_phrase
else:
    react_to_keyword = _do_not_react


__all__ = ["react_to_keyword"]
