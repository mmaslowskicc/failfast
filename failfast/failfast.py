import logging
from functools import wraps
from typing import Optional, List, Type

from failfast.store import Store, InProcessStore

logger = logging.getLogger(__name__)


class FailfastException(Exception):
    pass


def failfast(name: str,
             timeout_seconds: int = 300,
             store: Optional[Store] = None,
             exceptions: Optional[List[Type[BaseException]]] = None,
             enabled: bool = True):
    if exceptions is None:
        exceptions = [BaseException]

    if store is None:
        store = InProcessStore()

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not enabled:
                return fn(*args, **kwargs)

            is_already_broken = store.is_broken(name)
            if is_already_broken:
                logger.info("Failfast: preventing execution of %s due to previous errors", name)
                raise FailfastException("Failfast: disabled due to previous errors")
            try:
                return fn(*args, **kwargs)
            except BaseException as e:
                should_handle = any([isinstance(e, class_) for class_ in exceptions])
                if not should_handle:
                    raise
                store.set_broken(name, timeout_seconds)
                logger.info("Failfast: Disabling failing request for %d seconds due to: %s", timeout_seconds, str(e))
                raise

        return wrapper

    return decorator
