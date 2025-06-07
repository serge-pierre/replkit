"""
test_generic_repl.py

Unit tests for the GenericREPL class, including interpreter execution,
meta-commands, command recall, and REPL behavior under interruptions.
"""

import readline
import builtins
from replkit import GenericREPL


class DummyInterpreter:
    """Simple interpreter that records evaluated lines."""

    def __init__(self):
        self.executed = []

    def eval(self, line):
        # Record each line that reaches eval()
        self.executed.append(line)

    def get_keywords(self):
        return {"test", "help", "exit"}


def test_eval_execution(monkeypatch):
    """Test that a line is passed to eval() and REPL exits on .exit."""
    # Simulate: "test" → ".exit"
    inputs = iter(["test", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="> ", hello_sentence="")
    repl.loop()

    # Only "test" should have been executed; ".exit" stops the loop
    assert repl.interpreter.executed == ["test"]


def test_meta_exit(monkeypatch, capsys):
    """Test that .exit stops the REPL cleanly."""
    # Simulate: ".exit"
    inputs = iter([".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    captured = capsys.readouterr()
    assert "Bye!" in captured.out


def test_meta_help(monkeypatch, capsys):
    """Test that .help displays meta-command documentation."""
    # Simulate: ".help" → ".exit"
    inputs = iter([".help", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    out = capsys.readouterr().out
    assert "REPL meta-commands" in out
    assert ".exit" in out
    assert ".help" in out


def test_meta_history(monkeypatch, capsys):
    """Test that .history displays command history content."""
    # Ensure history contains one entry
    readline.clear_history()
    readline.add_history("run command")

    # Simulate: ".history" → ".exit"
    inputs = iter([".history", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    out = capsys.readouterr().out
    assert "run command" in out


def test_command_recall(monkeypatch, capsys):
    """Test command recall with !N uses the corresponding history line."""
    entries = ["first", "second"]
    # Simulate readline history containing "first", "second"
    monkeypatch.setattr(readline, "get_current_history_length", lambda: len(entries))
    monkeypatch.setattr(readline, "get_history_item", lambda i: entries[i - 1])
    # Stub out remove_history_item and add_history to avoid side effects
    monkeypatch.setattr(readline, "remove_history_item", lambda i: None)
    monkeypatch.setattr(readline, "add_history", lambda line: None)

    # Simulate: "!2" → ".exit"
    inputs = iter(["!2", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    interpreter = DummyInterpreter()
    repl = GenericREPL(interpreter=interpreter, prompt="", hello_sentence="")
    repl.loop()

    # "second" should have been passed to eval()
    assert interpreter.executed == ["second"]
    out = capsys.readouterr().out
    assert "# second" in out


def test_invalid_recall(monkeypatch, capsys):
    """Test recall with invalid index gives a warning."""
    # Simulate readline history_length = 2, but get_history_item always returns None
    monkeypatch.setattr(readline, "get_current_history_length", lambda: 2)
    monkeypatch.setattr(readline, "get_history_item", lambda i: None)

    # Simulate: "!5" → ".exit"
    inputs = iter(["!5", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    out = capsys.readouterr().out
    assert "No command at index 5" in out


def test_keyboard_interrupt(monkeypatch, capsys):
    """Simulate a Ctrl-C (KeyboardInterrupt) once, then exit."""
    sequence = [KeyboardInterrupt(), ".exit"]

    def fake_input(_):
        value = sequence.pop(0)
        # Now check for BaseException, so KeyboardInterrupt is raised
        if isinstance(value, BaseException):
            raise value
        return value

    monkeypatch.setattr(builtins, "input", fake_input)

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    out = capsys.readouterr().out
    # After KeyboardInterrupt, REPL should advise how to exit,
    # then the ".exit" input causes "Bye!".
    assert "Use .exit .quit or Ctrl-D to leave." in out
    assert "Bye!" in out


def test_eof_exit(monkeypatch, capsys):
    """Simulate a Ctrl-D (EOFError) once, then exit."""
    sequence = [EOFError(), ".exit"]

    def fake_input(_):
        value = sequence.pop(0)
        # Now check for BaseException, so EOFError is raised
        if isinstance(value, BaseException):
            raise value
        return value

    monkeypatch.setattr(builtins, "input", fake_input)

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()

    out = capsys.readouterr().out
    # On EOFError, REPL prints "Bye!" and exits immediately,
    # but in our sequence we supply ".exit" as fallback if needed.
    assert "Bye!" in out


def test_eval_error_handling(monkeypatch, capsys):
    class FailEval:
        def eval(self, line):
            raise RuntimeError("Simulated error")

        def get_keywords(self):
            return set()

    inputs = iter(["test", ".exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    repl = GenericREPL(interpreter=FailEval(), prompt="> ", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out
    assert "Error: Simulated error" in out


def test_process_line_unknown_command(monkeypatch):
    # Si aucun handler ne match, l'interpréteur doit recevoir la commande.
    class Recorder:
        def __init__(self):
            self.seen = []

        def eval(self, line):
            self.seen.append(line)

        def get_keywords(self):
            return set()

    repl = GenericREPL(interpreter=Recorder(), prompt="> ", hello_sentence="")
    repl.process_line("inconnu")
    assert "inconnu" in repl.interpreter.seen
