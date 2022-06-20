"""Host Voice Assistant config respresentation."""

from typing import Dict

import yaml

from voiceassistant.utils.datastruct import DottedDict


class Config(DottedDict):
    """Voice Assistant config parser."""

    def __init__(self, filepath: str) -> None:
        """Initialize config."""
        self._filepath = filepath
        self.reload()

    def reload(self) -> None:
        """Reload config."""
        super().__init__(self._read())

    def write(self, config_dict: Dict) -> None:
        """Write new config file from `config_dict`."""
        self._validate(config_dict)
        with open(self._filepath, "w") as config_file:
            yaml.dump(config_dict, config_file, default_flow_style=False)
        self.reload()

    def _read(self) -> Dict:
        """Get YAML config as dict."""
        with open(self._filepath) as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return self._validate(config)

    def _validate(self, config: Dict) -> Dict:
        """Validate config."""
        return config
