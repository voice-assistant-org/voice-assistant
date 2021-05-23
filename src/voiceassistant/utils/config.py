"""Config getter."""

from typing import Dict

import yaml

from voiceassistant.const import CONFIG_FILE_PATH

from .datastruct import DottedDict


def get_assistant_config() -> DottedDict:
    """Get YAML config as dotted dictionary."""
    with open(CONFIG_FILE_PATH) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        _validate_config(config)
        return DottedDict(config)


def set_assistant_config(config_dict: Dict) -> None:
    """Set config."""
    with open(CONFIG_FILE_PATH, "w") as config_file:
        _validate_config(config_dict)
        yaml.dump(config_dict, config_file, default_flow_style=False)


def _validate_config(config: Dict) -> None:
    """Validate config."""
    pass


Config = get_assistant_config()
