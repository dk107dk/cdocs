PATH:=bin/:${PATH}
.PHONY: \
    help \
    lint flake8 yapf yapf-diff \
    clean test clean_pyc compile clean_dist \
    clean_unit test_unit \

# --- Environment---

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(patsubst %/,%,$(dir $(MAKEFILE_PATH)))
PROJROOT := $(patsubst %/,%,$(dir $(MAKEFILE_DIR)))
UNITTESTS_DIR := $(MAKEFILE_DIR)/tests
DATE := $(shell date)

# --- Help ---

help:
	@echo
	@echo "Run on:" $(DATE)
	@echo
	@echo "Env vars:"
	@echo " " $(MAKEFILE_PATH)
	@echo " " $(MAKEFILE_DIR)
	@echo " " $(PROJROOT)
	@echo " " $(UNITTESTS_DIR)
	@echo " " $(INTEGRATIONTESTS_DIR)
	@echo " " $(SYSTEMTESTS_DIR)
	@echo " " $(BUILD_IMAGE)
	@echo "Available commands:"
	@echo "  lint                    run flake8 and yapf"
	@echo "    flake8                run flake8"
	@echo "    yapf                  run yapf and correct issues in-place"
	@echo "    yapf-diff             run yapf and display diff between existing and resolution"
	@echo "  clean                   remove files from last test run and *.pyc files"
	@echo "    clean_pyc             remove all *.pyc files"
	@echo "    clean_dist            clean distribution files"
	@echo "    clean_unit            remove files from last unit test run"
	@echo "  compile                 compile python source files"
	@echo "  test                    compile and run all tests"
	@echo "    test_unit             run all unit tests"
	@echo

# --- Utils ---

bash:
	bash

lint: flake8 yapf

flake8:
	flake8

yapf:
	yapf --in-place --recursive cdocs

# --- Compile and Test ---

clean: clean_pyc clean_dist clean_unit

test: compile test_unit

clean_pyc:
	@find $(MAKEFILE_DIR)/cdocs -name '*.pyc' -delete
	@find $(MAKEFILE_DIR)/cdocs -name '__pycache__' -delete

compile:
	@python -m compileall -f $(MAKEFILE_DIR)/cdocs

clean_dist:
	@rm -fr build dist cdocs.egg-info

clean_unit:
	@cd $(UNITTESTS_DIR) && rm -fr .coverage report_folder nosetests.xml cover

test_unit: clean_unit
test_unit:
	@cd $(UNITTESTS_DIR) && \
	  nosetests -c $(MAKEFILE_DIR)/setup.cfg --cover-html-dir=$(UNITTESTS_DIR)/report_folder


