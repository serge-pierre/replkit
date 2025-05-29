import tempfile
import os
from replkit.generic_repl import GenericREPL

class DummyInterpreter:
    def __init__(self):
        self.keywords = {"foo", "bar", "baz"}
        self.executed = []

    def eval(self, line):
        self.executed.append(line)

    def get_keywords(self):
        return self.keywords

def test_eval_execution(monkeypatch):
    # Simulate input/output with monkeypatch
    lines = iter(["foo", "exit"])

    monkeypatch.setattr("builtins.input", lambda _: next(lines))
    monkeypatch.setattr("readline.get_current_history_length", lambda: 0)

    interpreter = DummyInterpreter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_history:
        repl = GenericREPL(
            interpreter=interpreter,
            history_file=temp_history.name,
            prompt="",
            hello_sentence=""
        )
        repl.loop()

    assert interpreter.executed == ["foo"]
