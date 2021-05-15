"""Config getter."""

import yaml

from voiceassistant.const import CONFIG_FILE_PATH

from .datastruct import DottedDict


def _get_assistant_config() -> DottedDict:
    """Get YAML config as dotted dictionary."""
    with open(CONFIG_FILE_PATH) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        _validate_config(config)
        return DottedDict(config)


def _validate_config(config: DottedDict) -> None:
    """Validate config."""
    pass


Config = _get_assistant_config()
