from sentry_sdk import init

from sensitive_variables import sensitive_variables

init()


@sensitive_variables("password")
def login_user(username, password):
    print("Logging in " + username + " with " + password)


# TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
login_user(None, "secret123")
