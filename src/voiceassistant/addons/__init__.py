"""Host add-ons for different components."""

from typing import Any, Callable, Optional

from . import keyword, speech


def call_at(
    start: Optional[Callable] = None, end: Optional[Callable] = None
) -> Callable:
    """Wrap func to call specified function at the start and end."""

    def wrapper(func: Callable) -> Callable:
        def inner(*args: Any, **kwargs: Any) -> Any:
            if start is not None:
                start()

            result = func(*args, **kwargs)

            if end is not None:
                end()

            return result

        return inner

    return wrapper


__all__ = ["call_at", "keyword", "speech"]
