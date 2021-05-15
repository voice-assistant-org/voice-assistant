"""Voice assistant initial setup logic."""

import errno
import os

import yaml

from voiceassistant.const import (
    CONFIG_FILE_PATH,
    DEFAULT_CONFIG_DIR,
    GOOGLE_CREDENTIALS,
)


def pre_setup() -> None:
    """Do initial setup if needed."""
    if not os.path.exists(DEFAULT_CONFIG_DIR):
        try:
            os.makedirs(DEFAULT_CONFIG_DIR)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    sample_config = {
        "google_cloud": {"language_code": "en-US"},
        "aws": {
            "access_key_id": "YOUR_KEY_ID",
            "secret_access_key": "YOUR_SECRET_ACCESS_KEY",
            "region_name": "eu-west-2",
            "voice_id": "Brian",
        },
    }

    files_and_contents = (
        (GOOGLE_CREDENTIALS, ""),
        (CONFIG_FILE_PATH, yaml.dump(sample_config)),
    )

    for filepath, content in files_and_contents:
        if not os.path.exists(filepath):
            print(f"Creating {filepath}")
            with open(filepath, "w") as f:
                f.write(content)
