import functools
import logging
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def log(func: Callable[P, R]) -> Callable[P, R]:
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
