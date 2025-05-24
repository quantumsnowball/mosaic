import functools
import logging
import os
from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

ToBeWrapped = Callable[P, R]
Wrapped = Callable[P, R]
Wrapper = Callable[[ToBeWrapped[P, R]], Wrapped[P, R]]

LEVEL_CONTROL_ENV = 'MOSAIC_LOG_LEVEL'


# basicConfig, to be called on the root __init__
def setup_logger() -> None:
    logging.basicConfig(
        # use PYTHON_LOG_LEVEL shell env var to set level
        level=os.getenv(LEVEL_CONTROL_ENV, 'WARNING').upper(),
        # formatting
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# create logger
logger = logging.getLogger(__name__)


# decorator
def log_at_level(level: int) -> Wrapper[P, R]:
    def wrapper(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
        # wrapped function
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            # log info before funning the function
            logger.log(level, f"CALLED >> {func.__module__}.{func.__name__}()")

            # run the actual function
            result = func(*args, **kwargs)

            # log info after funning the function
            logger.log(level, f"          {func.__module__}.{func.__name__}() >> RETURN")

            # return the run result
            return result

        # return the wrapped function
        return wrapped

    # return the wrapper
    return wrapper


# namespace
class log:
    critical = log_at_level(CRITICAL)
    error = log_at_level(ERROR)
    warning = log_at_level(WARNING)
    info = log_at_level(INFO)
    debug = log_at_level(DEBUG)
    notset = log_at_level(NOTSET)
