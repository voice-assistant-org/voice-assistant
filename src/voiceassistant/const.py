"""Host constant variables."""

import os

DEFAULT_CONFIG_DIR = f"{os.path.expanduser('~')}/.config/voiceassistant"

# must be set in order to construct google.cloud.speech.SpeechClient
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = f"{DEFAULT_CONFIG_DIR}/google_credentials.json"

GOOGLE_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

CONFIG_FILE_PATH = os.environ.get(
    "VOICE_ASSISTANT_CONFIGURATION", f"{DEFAULT_CONFIG_DIR}/configuration.yaml"
)
