from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

ToBeWrapped = Callable[P, R]
Wrapped = Callable[P, R | None]
Wrapper = Callable[[ToBeWrapped[P, R], ], Wrapped[P, R]]


def preprocess(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
    # wrapped function
    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R | None:

        # checking here
        print(kwargs)
        print('check and modify kwargs here')

        # run the actual function, return as is
        return func(*args, **kwargs)

    # return the wrapped function
    return wrapped
