from time import perf_counter
from functools import wraps
from loguru import logger


def timeit(name: str):
    def timeit_inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = perf_counter()

            result = func(*args, **kwargs)

            end = perf_counter()

            logger.debug(f"{name} completed in {end - start:.4f}s")

            return result

        return wrapper
    return timeit_inner