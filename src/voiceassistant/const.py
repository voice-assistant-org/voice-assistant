"""Host constant variables."""

import argparse
import os


def _path(value: str) -> str:
    if os.path.exists(value):
        return value

    raise FileNotFoundError(f"Path {value} does not exist")


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Application port", type=int)
parser.add_argument("-up", "--userpath", help="User path", type=_path)

args = parser.parse_args()

GOOGLE_CREDENTIALS_FILENAME = "google_credentials.json"


USER_PATH = args.userpath or os.path.expanduser("~")
PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_CONFIG_DIR = f"{USER_PATH}/.config/voiceassistant"
CACHE_DIR = f"{USER_PATH}/.cache/voiceassistant/"
DATA_DIR = f"{PROJECT_PATH}/data"

CONFIG_FILE_PATH = os.environ.get(
    "VOICE_ASSISTANT_CONFIGURATION", f"{DEFAULT_CONFIG_DIR}/configuration.yaml"
)

PORT = args.port or 1507
