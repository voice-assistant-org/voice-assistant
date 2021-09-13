"""Voice Assistant interface base classes."""

import abc


class InterfaceIO(abc.ABC):
    """Voice Assistant user interface with support of input/output."""

    @abc.abstractmethod
    def input(self) -> str:
        """Get input from user."""
        raise NotImplementedError

    @abc.abstractmethod
    def output(self, text: str, cache: bool = False) -> None:
        """Provide output to user as `text`."""
        raise NotImplementedError
