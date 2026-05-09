from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


def timeit(name: str):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = perf_counter()

            try:
                return func(*args, **kwargs)
            finally:
                elapsed = perf_counter() - start
                logger.debug(f"{name} completed in {elapsed:.4f}s")

        return wrapper

    return decorator
