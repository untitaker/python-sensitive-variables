import functools
import nox

session = functools.partial(nox.session, reuse_venv=True)


@session(python=["2", "3", "pypy"])
def test(session):
    session.install("pytest")
    session.run("pytest", "tests/")


@session(python=["3"])
def lint(session):
    session.install("black")
    session.install("flake8")
    session.install("mypy")

    session.run("black", "--check", ".")
    session.run("flake8")
    session.run("mypy", "tests", "sensitive_variables.py")


@session(python=["3"])
def format(session):
    session.install("black")
    session.run("black", ".")
