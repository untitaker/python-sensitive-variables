from sensitive_variables import PLACEHOLDER, sensitive_variables, get_all_variables


def test_basic():
    is_test_func = True  # noqa

    @sensitive_variables("password")
    def login_user(username, password):
        is_inside_func = True  # noqa
        print("logging in " + username + password)

    try:
        login_user(None, "secret123")
    except TypeError:
        test_locals, wrapper_locals, locals = get_all_variables()
    else:
        assert False

    # Assert that we got the right frames
    assert test_locals["is_test_func"]
    assert locals["is_inside_func"]
    assert wrapper_locals["f"]

    # Assert real functionality
    assert locals["password"] == PLACEHOLDER
    assert "secret123" not in list(locals.values())
