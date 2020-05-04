import functools
import nox

session = functools.partial(nox.session, reuse_venv=True)


@session(python=["2.7", "3.7", "3.8", "pypy"])
def test(session):
    session.install("pytest")
    session.run("pytest", "tests/")


@session(python=["3.7"])
def lint(session):
    session.install("black")
    session.install("flake8")
    session.install("mypy")

    session.run("black", "--check", ".")
    session.run("flake8")
    session.run("mypy", "tests", "sensitive_variables")


@session(python=["3.7"])
def format(session):
    session.install("black")
    session.run("black", ".")


@session(python=["3.7"])
def release(session):
    session.install("twine")

    session.run("rm", "-rf", "dist/")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("twine", "upload", "dist/*")
