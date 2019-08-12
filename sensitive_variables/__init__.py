import sys
import platform

from functools import wraps

if False:
    from typing import Any
    from typing import Callable
    from typing import Iterator
    from typing import Optional
    from typing import Tuple
    from typing import TypeVar
    from typing import Dict
    from typing import Generator

    from types import FrameType
    from types import TracebackType

    F = TypeVar("F", bound=Callable[..., Any])


if platform.python_implementation() == "PyPy":
    from __pypy__ import locals_to_fast  # type: ignore
elif platform.python_implementation() == "CPython":
    import ctypes

    def locals_to_fast(frame):
        # type: (FrameType) -> None
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


__version__ = "0.1.0"


PLACEHOLDER = "<removed sensitive variable>"
ENABLED = True


def sensitive_variables(*variables, **config):
    # type: (*str, **Any) -> Callable[[F], F]

    def decorator(f):
        # type: (F) -> F

        @wraps(f)
        def sensitive_variables_wrapper(*args, **kwargs):
            # type: (*Any, **Any) -> Any
            __tracebackhide__ = True  # noqa
            __traceback_hide__ = True  # noqa
            try:
                return f(*args, **kwargs)
            except BaseException:
                if not ENABLED:
                    raise

                exc, value, tb = sys.exc_info()
                del args
                del kwargs
                _scrub_locals_from_traceback(tb, variables, **config)
                raise

        return sensitive_variables_wrapper  # type: ignore

    return decorator


def get_all_variables():
    # type: () -> Generator[Dict[Any, Any], None, None]
    for x in _iter_stacks(sys.exc_info()[-1]):
        yield x.f_locals


def _scrub_locals_from_traceback(traceback, names, depth=1):
    # type: (Optional[TracebackType], Tuple[str, ...], int) -> None
    for frame in _iter_stacks(traceback):
        if frame.f_globals.get("__name__") == __name__:
            continue

        if depth <= 0:
            break

        depth -= 1

        locals = frame.f_locals

        if locals.get("_sensitive_variables_scrubbed"):
            continue

        locals_modified = False

        if names:
            for name in names:
                if name in locals:
                    locals[name] = PLACEHOLDER
                    locals_modified = True
        else:
            locals.clear()
            locals_modified = True

        if locals_modified:
            locals_to_fast(frame)

        locals["_sensitive_variables_scrubbed"] = True


def _iter_stacks(tb):
    # type: (Optional[TracebackType]) -> Iterator[FrameType]
    tb_ = tb  # type: Optional[TracebackType]
    while tb_ is not None:
        yield tb_.tb_frame
        tb_ = tb_.tb_next
