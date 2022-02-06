"""Voice assistant initial setup logic."""

import shutil
from contextlib import suppress

from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR
from voiceassistant.utils.log import get_logger

_LOGGER = get_logger(__name__)


def pre_setup() -> None:
    """Do initial setup if needed."""
    with suppress(FileExistsError):
        shutil.copytree(f"{DATA_DIR}/sample_config/", DEFAULT_CONFIG_DIR)
        _LOGGER.info(f"Sample config files created at: {DEFAULT_CONFIG_DIR}")
