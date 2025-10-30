import functools
from typing import Callable, ParamSpec, TypeVar

from mosaic.utils.logging import logger

P = ParamSpec("P")
R = TypeVar("R")

ToBeWrapped = Callable[P, R]
Wrapped = Callable[P, R | None]
Wrapper = Callable[[ToBeWrapped[P, R], ], Wrapped[P, R]]


# catch any type of exception
def catch(
    *exceptions: type[BaseException],
) -> Wrapper:
    # decorator
    def wrapper(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
        # wrapped function
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R | None:
            try:
                # run the actual function, return as is
                return func(*args, **kwargs)
            except exceptions as e:
                # func is interrupted, None value is return
                logger.exception.debug(
                    f'{func.__module__}::{func.__qualname__}() caught {e.__class__}'
                )
                return None

        # return the wrapped function
        return wrapped

    # return the wrapper
    return wrapper
