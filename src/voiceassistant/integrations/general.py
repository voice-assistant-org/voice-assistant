"""Host general functionality integration."""

from __future__ import annotations

import os
import random
import subprocess
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING, List, Union

import yaml

from voiceassistant.addons.create import Addon, CoreAttribute, addon_end
from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR
from voiceassistant.exceptions import ConfigValidationError
from voiceassistant.integrations.base import Integration
from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Action, Skill, action, skill
from voiceassistant.utils.log import get_logger

if TYPE_CHECKING:
    from voiceassistant.config import Config
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.interfaces.base import InterfaceIO
    from voiceassistant.utils.datastruct import DottedDict

_LOGGER = get_logger(__name__)

NLP_DATAFILE = f"{DATA_DIR}/nlp/regex.yaml"


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up general functionality integration."""
    return GeneralFunctionality(config)


class GeneralFunctionality(Integration):
    """General functionality integration."""

    # general functionality comes with no name/domain
    name = None  # type: ignore

    def __init__(self, config: Config) -> None:
        """Init."""
        self._config = config

    @property
    def actions(self) -> List[Action]:
        """Return list of actions implemented by integration."""
        return [say]

    @property
    def skills(self) -> List[Skill]:
        """Return list of skills implemented by integration."""
        return [weather, current_time, reload_vass]

    @property
    def addons(self) -> List[Addon]:
        """Return list of regex intents implemented by integration."""
        if "sound" in self._config.triggerword:
            react_to_keyword = _react_by_sound
        elif "replies" in self._config.triggerword:
            react_to_keyword = _react_by_random_phrase
        else:
            react_to_keyword = _do_not_react

        return [react_to_keyword]

    @property
    def regex_intents(self) -> List[RegexIntent]:
        """Return list of regex intents implemented by integration."""
        with open(NLP_DATAFILE) as file:
            return [RegexIntent(**intent) for intent in yaml.safe_load(file)]


# addons


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _do_not_react(vass: VoiceAssistant) -> None:
    """Do nothing if reaction is not set in Config."""
    _LOGGER.info("Keyword detected")


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _react_by_random_phrase(vass: VoiceAssistant) -> None:
    """React to trigger word by a random reply phrase."""
    _LOGGER.info("Keyword detected")
    vass.interfaces.speech.output(text=random.choice(vass.config.triggerword.replies), cache=True)


@addon_end(CoreAttribute.KEYWORD_WAIT, name="keyword_react")
def _react_by_sound(vass: VoiceAssistant) -> None:
    """React to trigger detection word."""
    _LOGGER.info("Keyword detected")
    subprocess.Popen(
        ["mpg123", _get_soundfile_path(vass.config.triggerword.sound)],
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


# skills


@skill("weather")
def weather(entities: DottedDict, interface: InterfaceIO) -> None:
    """Get weather sample skill."""
    if entities.get("city"):
        interface.output(f"weather in {entities.city} is nice")
    else:
        interface.output("weather is nice")


@skill("current-time")
def current_time(interface: InterfaceIO) -> None:
    """Get current time."""
    time_now = datetime.now().strftime("%H:%M")
    interface.output(f"It's {time_now}")


@skill("reload")
def reload_vass(vass: VoiceAssistant, interface: InterfaceIO) -> None:
    """Reload Voice Assistant."""
    try:
        vass.load_components()
        interface.output("I am now reloaded")
    except yaml.scanner.ScannerError:
        interface.output("Aborting, configuration YAML file is invalid.")


# actions
@action("say")
def say(vass: VoiceAssistant, text: Union[str, List[str]]) -> None:
    """Say a text or randamly chosen text."""
    if isinstance(text, str):
        vass.interfaces.speech.output(text)
    elif isinstance(text, list):
        vass.interfaces.speech.output(random.choice(text))
