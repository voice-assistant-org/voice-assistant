"""Host device volume control utils."""


from types import TracebackType
from typing import Any, Type

import alsaaudio


class _Mixer:
    """Mixer with context handling."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Init."""
        self._alsamixer = alsaaudio.Mixer(*args, **kwargs)

    def __enter__(self) -> alsaaudio.Mixer:
        """Enter."""
        return self._alsamixer

    def __exit__(
        self, type: Type[BaseException], value: BaseException, traceback: TracebackType
    ) -> None:
        """Close mixer."""
        self._alsamixer.close()


def set_volume(level: int) -> None:
    """Set master volume."""
    with _Mixer() as mixer:
        mixer.setvolume(level)


def get_volume() -> int:
    """Get master volume."""
    with _Mixer() as mixer:
        return mixer.getvolume()[0]  # type: ignore


def set_mute(mute: bool) -> None:
    """Set mute, 1 for mute and 0 for unmute."""
    with _Mixer() as mixer:
        mixer.setmute(int(mute))


def is_muted() -> bool:
    """Check if volume is muted."""
    with _Mixer() as mixer:
        return 0 not in mixer.getmute()
