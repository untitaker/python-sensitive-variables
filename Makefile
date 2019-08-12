format:
	nox -e format
.PHONY: format

lint:
	nox -e lint
.PHONY: lint

test-all:
	nox -e test
.PHONY: test-all

release:
	nox -e release
.PHONY: release
