"""Voice Assistant interface base classes."""

from abc import ABC, abstractmethod


class BaseInterface(ABC):
    """Base Voice Assistant interface."""

    @abstractmethod
    def run(self) -> None:
        """Run interface."""
        pass


class InterfaceIO(BaseInterface):
    """Voice Assistant user interface with support of input/output."""

    @abstractmethod
    def input(self) -> str:
        """Get input from user."""
        return ""

    @abstractmethod
    def output(self, text: str, cache: bool = False) -> None:
        """Provide output to user as `text`."""
        pass
