"""Voice Assistant interfaces."""

from .http import HttpInterface
from .speech import SpeechInterface

__all__ = ["SpeechInterface", "HttpInterface"]
