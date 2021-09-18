"""Voice assistant initial setup logic."""

import shutil
from contextlib import suppress

from voiceassistant.const import DATA_DIR, DEFAULT_CONFIG_DIR


def pre_setup() -> None:
    """Do initial setup if needed."""
    with suppress(FileExistsError):
        shutil.copytree(f"{DATA_DIR}/sample_config/", DEFAULT_CONFIG_DIR)
        print(f"Sample config files created at: {DEFAULT_CONFIG_DIR}")
