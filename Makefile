#
# Settings
#

BUILD_DIR = build
SOURCE_DIRS = cryptobob
LINTER_CONFIGS = https://git.confirm.ch/confirm/guidelines/raw/master/configs
PYPI_INDEX = https://pypi.confirm.ch/

.PHONY: build

#
# Cleanup
#

clean: clean-cache clean-test clean-build clean-venv

clean-cache:
	find . -name '__pycache__' -delete

clean-test:
	rm -vf .coverage .coveragerc .isort.cfg .pylintrc tox.ini

clean-build:
	rm -vrf $(BUILD_DIR) .eggs *.egg-info

clean-venv:
	rm -vrf .venv

#
# Install
#

venv:
	python3 -m venv .venv

develop:
	pip3 install -i $(PYPI_INDEX) -e .[dev]

install:
	pip3 install -i $(PYPI_INDEX) .

#
# Development
#

isort:
	curl -sSfLo .isort.cfg $(LINTER_CONFIGS)/isort.cfg
	isort $(SOURCE_DIRS)

#
# Test
#

test-isort:
	curl -sSfLo .isort.cfg $(LINTER_CONFIGS)/isort.cfg
	isort -c --diff $(SOURCE_DIRS)

test-pycodestyle:
	curl -sSfLo tox.ini $(LINTER_CONFIGS)/tox.ini
	pycodestyle $(SOURCE_DIRS)

test-pylint:
	curl -sSfLo .pylintrc $(LINTER_CONFIGS)/pylintrc
	pylint $(SOURCE_DIRS)

test-packages:
	pip-audit

test: test-isort test-pycodestyle test-pylint test-packages

#
# Build
#

sdist:
	./setup.py sdist -d $(BUILD_DIR)

wheel:
	./setup.py bdist_wheel -d $(BUILD_DIR)

build: sdist wheel
