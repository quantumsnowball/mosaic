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
LOGGER_SELECTION_ENV = 'MOSAIC_LOGGER'


# create logger
class logger:
    _loggers = dict(
        base=logging.getLogger('base'),
        exception=logging.getLogger('exception'),
    )
    base = _loggers['base']
    exception = _loggers['exception']

    @classmethod
    def select(cls, selection: str) -> None:
        # parse inputs
        parts = map(str.strip, selection.split(','))
        names = set(filter(lambda x: len(x) > 0, parts))

        # find valid selection
        selected = names & set(cls._loggers)

        # if nothing valid selected, return
        if len(selected) == 0:
            return

        # display the selected, suppress the ignored
        for name, logger in cls._loggers.items():
            if name in selected:
                logger.setLevel(DEBUG)
            else:
                logger.setLevel(CRITICAL)


# basicConfig, to be called on the root __init__
def setup_logger() -> None:
    # level selection
    # e.g. usage: MOSAIC_LOG_LEVEL=DEBUG
    logging.basicConfig(
        # use PYTHON_LOG_LEVEL shell env var to set level
        level=os.getenv(LEVEL_CONTROL_ENV, 'WARNING').upper(),
        # formatting
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # logger selection
    # e.g. usage: MOSAIC_LOGGER=base,exception
    logger.select(os.getenv(LOGGER_SELECTION_ENV, ''))


# decorator
def log_at_level(level: int) -> Wrapper[P, R]:
    def wrapper(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
        # wrapped function
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            # log info before funning the function
            logger.base.log(
                level,
                f"CALLED >> {func.__module__}.{func.__name__}()"
            )

            # run the actual function
            result = func(*args, **kwargs)

            # log info after funning the function
            logger.base.log(
                level,
                f"          {func.__module__}.{func.__name__}() >> RETURN"
            )

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
