"""Main file."""

from voiceassistant.exceptions import SetupIncomplete
from voiceassistant.setup import pre_setup
from voiceassistant.utils.log import get_logger

_LOGGER = get_logger(__name__)


def main() -> None:
    """Run application."""
    pre_setup()

    from voiceassistant.core import VoiceAssistant

    try:
        vass = VoiceAssistant()
        vass.run()
    except SetupIncomplete as e:
        _LOGGER.error(f"Voice Assistant setup is incomplete:\n{e}")


if __name__ == "__main__":
    main()
