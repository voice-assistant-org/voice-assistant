"""Host Add-ons for Voice Assistant components.

Add-ons:
 - are added by wrapping methods of different Voice Assistant components
 - can be conditionally added by integrations e.g. if Spotify integration
   is active, music volume will go down when VA is listening or talking
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from . import keyword_addon
from .create import Addon, CoreAttribute

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


_INTERNAL_ADDONS = [
    keyword_addon.react_to_keyword,
]


class AddonsComponent:
    """Addons Component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass

        for addon in _INTERNAL_ADDONS:
            self.add(addon)

    def add(self, addon: Addon) -> None:
        """Enable addon by wrapping one of methods in core object."""
        print(f"Adding addon: {addon.name}")

        method = self._get_core_attr(addon.core_attr)
        wrapped_method = _wrap(
            to_wrap=method,
            with_func=addon.func,  # type: ignore
            at_start=addon.at_start,
            vass=self._vass,
        )
        self._set_core_attr(addon.core_attr, wrapped_method)

    def _get_core_attr(self, core_attr: CoreAttribute) -> Any:
        """Get an attribute of an object located at the attribute path."""
        temp = self._vass
        for key in core_attr.value:
            temp = getattr(temp, key)
        return temp

    def _set_core_attr(self, core_attr: CoreAttribute, value: Any) -> None:
        """Set an attribute of an object located at the attribute path."""
        temp = self._vass
        path = core_attr.value
        for key in path:
            if not hasattr(temp, key):
                raise AttributeError(f"'{temp}' doesn't have attribute '{key}', can't assign")
            if key == path[-1]:
                setattr(temp, key, value)
            else:
                temp = getattr(temp, key)


def _wrap(
    to_wrap: Callable,
    with_func: Callable[[VoiceAssistant], None],
    at_start: bool,
    vass: VoiceAssistant,
) -> Callable:
    """Wrap `to_wrap` function with another function `with_func`."""
    if at_start:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            with_func(vass)
            to_wrap(*args, **kwargs)

    else:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            result = to_wrap(*args, **kwargs)
            with_func(vass)
            return result

    return wrapped


__all__ = ["AddonsComponent"]
