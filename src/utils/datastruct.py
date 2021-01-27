"""Host custom data structures used in the project."""

from six.moves import queue


class DottedDict(dict):
    """Python dict with dot-syntax added on top."""

    def __getattr__(self, key):
        try:
            attr = self[key]
            if isinstance(attr, dict):
                return DottedDict(attr)
            else:
                return attr
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        try:
            self[key] = value
        except KeyError:
            raise AttributeError(key)


class RollingWindowQueue:
    def __init__(self, size):
        self.size = size
        self._current_size = 0
        self._buffer = queue.Queue()
        self._size_limit_enabled = True

    def disable_size_limit(self):
        self._size_limit_enabled = False

    def put(self, element):
        self._buffer.put(element)
        self._current_size += 1
        if self._size_limit_enabled and self._current_size > self.size:
            self._buffer.get()

    def get(self, block=True):
        self._current_size -= 1
        return self._buffer.get(block=block)
