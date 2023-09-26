#!/usr/bin/env python3

import os

import nox

nox.options.sessions = ["lint", "typecheck"]
nox.options.reuse_existing_virtualenvs = True
os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})


def pdm_install(session, group):
    session.run_always("pdm", "install", "-G", group, external=True, silent=True)


@nox.session
def lint(session):
    pdm_install(session, "dev")
    session.run("pre-commit", "run")


@nox.session
def typecheck(session):
    pdm_install(session, "dev")
    session.run("mypy", "src/")


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def test(session):
    pdm_install(session, "test")
    session.run("pytest")
