import gc

import pytest

from sensitive_variables import PLACEHOLDER, sensitive_variables, get_all_variables


ITERATION_COUNT = 1000


@pytest.fixture
def no_cyclic_references():
    gc.disable()
    gc.collect()

    def inner(f):
        old_objects = len(gc.get_objects())
        for _ in range(ITERATION_COUNT):
            f()

        assert len(gc.get_objects()) - old_objects < ITERATION_COUNT

    yield inner

    gc.enable()
    gc.collect()


def test_basic(no_cyclic_references):
    def f():
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

    no_cyclic_references(f)
