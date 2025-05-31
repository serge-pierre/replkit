"""
test_completer.py

Unit tests for the REPLCompleter class.

These tests validate:
- keyword completion from interpreter
- meta-command completion
- history-based suggestions
- combinations of the above
"""

import readline
from replkit import REPLCompleter


# --- Dummy interpreter for keyword testing ---
class DummyInterpreter:
    def __init__(self):
        self.words = {"add", "drop", "duplicate", "run", "load", "eval"}

    def get_keywords(self):
        return self.words


# --- Utility to collect all completions for a given input prefix ---
def collect_completions(completer, text):
    """Returns a list of all matches for a given text prefix."""
    results = []
    state = 0
    while True:
        match = completer.complete(text, state)
        if match is None:
            break
        results.append(match)
        state += 1
    return results


def test_completer_interpreter_keywords():
    """Ensure interpreter keywords are completed correctly."""
    interpreter = DummyInterpreter()
    completer = REPLCompleter(interpreter, meta_commands=set())  # no meta
    results = collect_completions(completer, "d")
    assert "drop" in results
    assert "duplicate" in results
    assert "add" not in results  # should not match "d"


def test_completer_meta_commands():
    """Test completion with meta-commands only, no keywords."""

    class NoKeywordInterpreter:
        def get_keywords(self):
            return set()

    meta = {".exit", ".quit", ".help", ".history"}
    completer = REPLCompleter(NoKeywordInterpreter(), meta_commands=meta)
    results = collect_completions(completer, ".h")
    assert ".help" in results
    assert ".history" in results
    assert ".exit" not in results  # does not match ".h"


def test_completer_history(monkeypatch):
    """Verify completion suggestions include words from readline history."""

    class NoKeywordInterpreter:
        def get_keywords(self):
            return set()

    entries = ["run this", "drop that", "exit now"]

    monkeypatch.setattr(readline, "get_current_history_length", lambda: len(entries))
    monkeypatch.setattr(readline, "get_history_item", lambda i: entries[i - 1])

    completer = REPLCompleter(NoKeywordInterpreter(), meta_commands=set())
    results = collect_completions(completer, "d")
    assert "drop" in results  # from "drop that"
    assert "drop that" not in results  # full line shouldn't be suggested
    assert "that" not in results  # only first word of entry matched


def test_completer_combined(monkeypatch):
    """Test completion when interpreter, history, and meta-commands are all active."""
    entries = ["history", "drop"]
    monkeypatch.setattr(readline, "get_current_history_length", lambda: len(entries))
    monkeypatch.setattr(readline, "get_history_item", lambda i: entries[i - 1])

    class MixedInterpreter:
        def get_keywords(self):
            return {"drop", "push", "pop"}

    meta = {".help", ".exit", ".clear", ".reload"}

    completer = REPLCompleter(MixedInterpreter(), meta_commands=meta)
    results = collect_completions(completer, "p")

    assert "push" in results
    assert "pop" in results
    assert "drop" not in results  # doesn't start with "p"
    assert ".exit" not in results  # doesn't start with "p"


def test_completer_meta_and_keywords():
    """Test combined completions for '.' prefix (meta + keywords)."""
    completer = REPLCompleter(DummyInterpreter())
    results = collect_completions(completer, ".")

    assert ".exit" in results
    assert ".help" in results
    assert ".reload" in results
    assert "run" not in results  # not a meta-command, doesn't start with '.'
