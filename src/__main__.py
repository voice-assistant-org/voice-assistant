""""Main file."""

import os

from src.core import run_voice_assistant
from src.exceptions import AssistantBaseError


def _check_envvar():
    required_envvar = (
        "GOOGLE_APPLICATION_CREDENTIALS",
        "VOICE_ASSISTANT_CONFIGURATION",
    )
    missing_envvar = [var for var in required_envvar if var not in os.environ]
    print("---", missing_envvar)

    if missing_envvar:
        raise AssistantBaseError(
            f"Missing environment variables: {', '.join(missing_envvar)}"
        )


if __name__ == "__main__":
    _check_envvar()
    run_voice_assistant()
