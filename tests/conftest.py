# tests/conftest.py
import os
import pytest

HISTORY_FILE = ".repl_history"
ALIASES_FILE = ".repl_aliases"


@pytest.fixture(autouse=True)
def cleanup_repl_history():
    yield
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


@pytest.fixture(autouse=True)
def cleanup_repl_aliases():
    yield
    if os.path.exists(ALIASES_FILE):
        os.remove(ALIASES_FILE)
