"""Host device volume control utils."""

from functools import wraps
from types import TracebackType
from typing import Any, Callable, Type

import alsaaudio


def _handle_alsa_error(func: Callable) -> Callable:
    """Wrap funcion to handle alsa errors on some devices."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except alsaaudio.ALSAAudioError:
            return None

    return wrapper


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


@_handle_alsa_error
def set_volume(level: int) -> None:
    """Set master volume."""
    with _Mixer() as mixer:
        mixer.setvolume(level)


@_handle_alsa_error
def get_volume() -> int:
    """Get master volume."""
    with _Mixer() as mixer:
        return mixer.getvolume()[0]  # type: ignore


@_handle_alsa_error
def set_mute(mute: bool) -> None:
    """Set mute, 1 for mute and 0 for unmute."""
    with _Mixer() as mixer:
        mixer.setmute(int(mute))


@_handle_alsa_error
def is_muted() -> bool:
    """Check if volume is muted."""
    with _Mixer() as mixer:
        return 0 not in mixer.getmute()
