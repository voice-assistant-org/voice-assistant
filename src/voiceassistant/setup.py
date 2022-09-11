"""Voice assistant initial setup logic."""

import os
import shutil
from contextlib import suppress

from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR, GOOGLE_CREDENTIALS_FILENAME
from voiceassistant.utils.log import get_logger

_LOGGER = get_logger(__name__)


def pre_setup() -> None:
    """Do initial setup if needed."""
    with suppress(FileExistsError):
        shutil.copytree(f"{DATA_DIR}/sample_config/", DEFAULT_CONFIG_DIR)
        _LOGGER.info(f"Sample config files created at: {DEFAULT_CONFIG_DIR}")

    # must be set in order to construct google.cloud.speech.SpeechClient
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"
        ] = f"{DEFAULT_CONFIG_DIR}/{GOOGLE_CREDENTIALS_FILENAME}"
