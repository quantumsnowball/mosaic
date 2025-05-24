import functools
import logging
import os
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


# basicConfig, to be called on the root __init__
def setup_logger() -> None:
    logging.basicConfig(
        # use PYTHON_LOG_LEVEL shell env var to set level
        level=os.getenv('PYTHON_LOG_LEVEL', 'WARNING').upper(),
        # formatting
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# create logger
logger = logging.getLogger(__name__)


# decorator
def log(func: Callable[P, R]) -> Callable[P, R]:
    # wrapped function
    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        # log info before funning the function
        logger.info(f"CALLED >> {func.__module__}.{func.__name__}()")

        # run the actual function
        result = func(*args, **kwargs)

        # log info after funning the function
        logger.info(f"          {func.__module__}.{func.__name__}() >> RETURN")

        # return the run result
        return result

    # return the wrapped function
    return wrapped
