import readline
from replkit.generic_repl import REPLCompleter

# --- Dummy interpreter ---
class DummyInterpreter:
    def __init__(self):
        self.words = {"add", "drop", "duplicate"}

    def get_keywords(self):
        return self.words

# --- Utility function for completion ---
def collect_completions(completer, text):
    results = []
    state = 0
    while True:
        match = completer.complete(text, state)
        if match is None:
            break
        results.append(match)
        state += 1
    return results

# --- Test 1: interpreter keywords only ---
def test_completer_interpreter_keywords():
    interpreter = DummyInterpreter()
    completer = REPLCompleter(interpreter, meta_commands=set())  # no meta
    results = collect_completions(completer, "d")
    assert "drop" in results
    assert "duplicate" in results
    assert "add" not in results

# --- Test 2: meta-commands only ---
def test_completer_meta_commands():
    class NoKeywordInterpreter:
        def get_keywords(self):
            return set()

    meta = {"exit", "quit", "history", "help"}
    completer = REPLCompleter(NoKeywordInterpreter(), meta_commands=meta)
    results = collect_completions(completer, "h")
    assert "help" in results
    assert "history" in results
    assert "exit" not in results

# --- Test 3: history words only ---
def test_completer_history(monkeypatch):
    class NoKeywordInterpreter:
        def get_keywords(self):
            return set()

    # Fake history with readline.get_current_history_length / get_history_item
    entries = ["run this", "drop that", "exit now"]

    monkeypatch.setattr(readline, "get_current_history_length", lambda: len(entries))
    monkeypatch.setattr(readline, "get_history_item", lambda i: entries[i - 1])

    completer = REPLCompleter(NoKeywordInterpreter(), meta_commands=set())
    results = collect_completions(completer, "d")
    assert "drop" in results
    assert "drop that" not in results  # split words, not full lines
    assert "that" not in results

# --- Test 4: combined sources ---
def test_completer_combined(monkeypatch):
    entries = ["history", "drop"]
    monkeypatch.setattr(readline, "get_current_history_length", lambda: len(entries))
    monkeypatch.setattr(readline, "get_history_item", lambda i: entries[i - 1])

    class MixedInterpreter:
        def get_keywords(self):
            return {"drop", "push", "pop"}

    meta = {"help", "exit"}

    completer = REPLCompleter(MixedInterpreter(), meta_commands=meta)
    results = collect_completions(completer, "p")

    assert "push" in results
    assert "pop" in results
    assert "drop" not in results  # does not match "p"
    assert "exit" not in results  # does not match "p"
