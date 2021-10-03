"""Host constant variables."""

import os

DEFAULT_CONFIG_DIR = f"{os.path.expanduser('~')}/.config/voiceassistant"
PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = f"{PROJECT_PATH}/data"
CACHE_DIR = f"{PROJECT_PATH}/../../.vass_cache"

# must be set in order to construct google.cloud.speech.SpeechClient
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{DEFAULT_CONFIG_DIR}/google_credentials.json"

GOOGLE_CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

CONFIG_FILE_PATH = os.environ.get(
    "VOICE_ASSISTANT_CONFIGURATION", f"{DEFAULT_CONFIG_DIR}/configuration.yaml"
)

PORT = 5050
