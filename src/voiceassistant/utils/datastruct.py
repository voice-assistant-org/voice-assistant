"""Host custom data structures used in the project."""

from typing import Any

from voiceassistant.exceptions import DottedAttribureError


class DottedDict(dict):
    """Python dict with dot-syntax added on top."""

    def __getattr__(self, key: str) -> Any:
        """Get attribute."""
        try:
            attr = self[key]
            if isinstance(attr, dict):
                return DottedDict(attr)
            elif isinstance(attr, list):
                return [DottedDict(i) if isinstance(i, dict) else i for i in attr]
            else:
                return attr
        except KeyError as e:
            raise DottedAttribureError(e)

    def __setattr__(self, key: str, value: Any) -> None:
        """Set attribute."""
        try:
            self[key] = value
        except KeyError as e:
            raise DottedAttribureError(e)


class RecognitionString(str):
    """Modify string object to have `is_final` attribute.

    Required to differentiate between cases where
    continious speech recognition is still running
    or whether recognition result is final.
    """

    is_final = False

    def __new__(cls, value: str, is_final: bool):  # type: ignore
        """Create recognition string object."""
        self_obj = str.__new__(cls, value)
        self_obj.is_final = is_final
        return self_obj
