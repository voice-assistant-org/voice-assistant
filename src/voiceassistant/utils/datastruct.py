"""Host custom data structures used in the project."""

from typing import Any

from six.moves import queue


class DottedDict(dict):
    """Python dict with dot-syntax added on top."""

    def __getattr__(self, key: str) -> Any:
        """Get attribute."""
        try:
            attr = self[key]
            if isinstance(attr, dict):
                return DottedDict(attr)
            elif isinstance(attr, list):
                return [
                    DottedDict(i) if isinstance(i, dict) else i for i in attr
                ]
            else:
                return attr
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key: str, value: Any) -> None:
        """Set attribute."""
        try:
            self[key] = value
        except KeyError as e:
            raise AttributeError(e)


class RollingWindowQueue:
    """Rolling window queue."""

    def __init__(self, size: int):
        """Init."""
        self.size = size
        self._current_size = 0
        self._buffer: queue.Queue = queue.Queue()
        self._size_limit_enabled = True

    def disable_size_limit(self) -> None:
        """Convert to unlimited size Queue."""
        self._size_limit_enabled = False

    def put(self, element: Any) -> None:
        """Put element to the queue."""
        self._buffer.put(element)
        self._current_size += 1
        if self._size_limit_enabled and self._current_size > self.size:
            self._buffer.get()

    def get(self, block: bool = True) -> Any:
        """Get element from the queue."""
        self._current_size -= 1
        return self._buffer.get(block=block)
