import functools
import logging
import os
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
        function=logging.getLogger('function'),
        exception=logging.getLogger('exception'),
    )
    base = _loggers['base']
    function = _loggers['function']
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
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.CRITICAL)


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
def trace_function(level: int) -> Wrapper:
    def wrapper(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
        # wrapped function
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            # log info before funning the function
            logger.function.log(
                level,
                f"CALLED >> {func.__module__}::{func.__qualname__}()"
            )

            # run the actual function
            result = func(*args, **kwargs)

            # log info after funning the function
            logger.function.log(
                level,
                f"          {func.__module__}::{func.__qualname__}() >> RETURN"
            )

            # return the run result
            return result

        # return the wrapped function
        return wrapped

    # return the wrapper
    return wrapper


# helper
trace = trace_function(logging.DEBUG)


# namespace
class log:
    # general log function at base logger
    critical = logger.base.critical
    error = logger.base.error
    warning = logger.base.warning
    info = logger.base.info
    debug = logger.base.debug
