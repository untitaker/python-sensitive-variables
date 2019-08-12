import sys
import platform

from functools import wraps

if False:
    from typing import Optional
    from typing import Iterator

    from types import FrameType
    from types import TracebackType


if platform.python_implementation() == "PyPy":
    from __pypy__ import locals_to_fast  # type: ignore
elif platform.python_implementation() == "CPython":
    import ctypes

    def locals_to_fast(frame):
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


PLACEHOLDER = "<removed sensitive variable>"


def sensitive_variables(*variables, **config):
    def decorator(f):
        @wraps(f)
        def sensitive_variables_wrapper(*args, **kwargs):
            __tracebackhide__ = True  # noqa
            __traceback_hide__ = True  # noqa
            try:
                return f(*args, **kwargs)
            except BaseException:
                exc, value, tb = sys.exc_info()
                del args
                del kwargs
                _scrub_locals_from_traceback(tb, variables, **config)
                raise

        if variables:
            sensitive_variables_wrapper.sensitive_variables = variables
        else:
            sensitive_variables_wrapper.sensitive_variables = "__ALL__"

        return sensitive_variables_wrapper

    return decorator


def _scrub_locals_from_traceback(traceback, names, depth=1):
    for frame in _iter_stacks(traceback):
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
