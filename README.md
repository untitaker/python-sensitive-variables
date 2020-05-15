# sensitive_variables - strip local variables in tracebacks

[![Build Status](https://travis-ci.com/untitaker/python-sensitive-variables.svg?token=KCykhJnWfRnhkGxeQkqY&branch=master)](https://travis-ci.com/untitaker/python-sensitive-variables)
[![PyPi page link -- version](https://img.shields.io/pypi/v/sensitive-variables.svg)](https://pypi.python.org/pypi/sensitive-variables)

`sensitive_variables` is a decorator you can apply to your functions to
prevent certain local variables from being read by debugging tools, such as the
[Django crash reporter](https://docs.djangoproject.com/en/2.2/howto/error-reporting/) or [Sentry](https://sentry.io/).

Unlike Django's `sensitive_variables` it is independent of the web framework
you use and also does not rely on debugging tools to know about the decorator
for things to work.

## Usage:

### Basic

```python
from sentry_sdk import init

from sensitive_variables import sensitive_variables

init()

@sensitive_variables('password')
def login_user(username, password):
    print("Logging in " + username + " with " + password)

# TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
login_user(None, "secret123")
```

results in:

<img src=https://raw.githubusercontent.com/untitaker/python-sensitive-variables/master/demo.png width=533 alt="Picture of Sentry's traceback view where each frame contains local variables. The password variable contains a placeholder instead of the actual value." />

### Custom scrub function

`sensitive_varibles` can receive a custom_scrub_fn parameter which will ba called for each local variable.
It receives the local value and variable name and must return `value_has_changed, new_value`.
Where value_has_changed is a boolean which represents the value being changed or not and new_value is the new value.

You can use this to extend scrub for dictionaries and any other custom type.

Example:
```python
from sentry_sdk import init

from sensitive_variables import sensitive_variables

init()

def my_scrub_fn(value, variable_name):
    if variable_name == 'password':
        return True, 'scrubbed-value'
    return False, value


@sensitive_variables(custom_scrub_fn=my_scrub_fn)
def login_user(username, password):
    print("Logging in " + username + " with " + password)

# TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
login_user(None, "secret123")
```

## How does it work?

When the decorated function throws an exception, `sensitive_variables` walks through the traceback, removes sensitive data from `frame.f_locals` calling custom_scrub_fn so custom processing can be made and reraises the exception.

This is usually not problematic because a function that just threw an exception is unlikely to still use its local variables.

## Why would I use this over Django's decorator?

Django has a decorator also called `sensitive_variables`, which this package is inspired by. It sets an attribute on the function object that contains the variable names.

Debugging tools have to know about this attribute and respect it. For anything outside of the Django world, this is unlikely to be the case.

The decorator in this package will always work because it actually modifies your locals.

## Why would I use this over Sentry's datascrubbing options?

* This decorator does not couple your configuration for what is sensitive data to a specific crash reporting tool.

* Behavior of the decorator is easily unit-testable (see `tests/` folder).

## Why would I not use this?

This decorator inherently requires custom code for each Python implementation. Currently this is only tested against CPython 2.7, CPython 3.7, CPython 3.8 and PyPy 2.7.

## License

Licensed under the MIT, see ``LICENSE``.
