"""Main file."""

from voiceassistant.exceptions import SetupIncomplete
from voiceassistant.setup import pre_setup


def main() -> None:
    """Run application."""
    pre_setup()

    from voiceassistant.core import VoiceAssistant

    try:
        vass = VoiceAssistant()
        vass.run()
    except SetupIncomplete as e:
        print(f"Voice Assistant setup is incomplete:\n{e}")


if __name__ == "__main__":
    main()
