# tests/conftest.py
import os
import pytest

HISTORY_FILE = ".repl_history"

@pytest.fixture(autouse=True)
def cleanup_repl_history():
    yield
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
