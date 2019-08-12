# sensitive_variables - strip local variables in tracebacks

[![Build Status](https://travis-ci.com/untitaker/python-sensitive-variables.svg?token=KCykhJnWfRnhkGxeQkqY&branch=master)](https://travis-ci.com/untitaker/python-sensitive-variables)

`sensitive_variables` is a decorator you can apply to your functions to
prevent certain local variables from being read by debugging tools, such as the
[Django crash reporter](https://docs.djangoproject.com/en/2.2/howto/error-reporting/) or [Sentry](https://sentry.io/).

Unlike Django's `sensitive_variables` it is independent of the web framework
you use and also does not rely on debugging tools to know about the decorator
for things to work.

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

<img src=demo.png width=576 />

## How does it work?

When the decorated function throws an exception, `sensitive_variables` walks through the traceback, removes sensitive data from `frame.f_locals` and reraises the exception.

This is usually not problematic because a function that just threw an exception is unlikely to still use its local variables.

## Why would I use this over Django's decorator?

Django has a decorator also called `sensitive_variables`, which this package is inspired by. It adds an attribute to the function that contains the variable names.

Debugging tools have to know about this attribute and respect it. For anything outside of the Django world, this is unlikely to be the case.

This decorator will always work because it actually modifies your locals.

## Why would I use this over Sentry's datascrubbing options?

* This decorator does not couple your configuration for what is sensitive data to a specific crash reporting tool.

* Datascrubbing is easily unit-testable (see `tests/` folder).

## License

Licensed under the MIT, see ``LICENSE``.
