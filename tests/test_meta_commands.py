"""
test_meta_commands.py

Unit tests for REPL meta-commands in GenericREPL, including:
- .exit and .quit to leave the loop
- .help to display built-in commands
- .history to show stored history
- .clear to clear the screen (no-op in tests)
- .reload to re-run the init-file contents
"""

import os
import readline
import builtins
from replkit import GenericREPL


class DummyInterpreter:
    """A dummy interpreter that simply records each line passed to eval()."""

    def __init__(self):
        self.executed = []

    def eval(self, line):
        """Record the given line for later verification."""
        self.executed.append(line)

    def get_keywords(self):
        """Dummy keywords (unused in these tests)."""
        return {"foo", "bar"}


def test_meta_exit_and_quit(monkeypatch, capsys):
    """Verify that both '.exit' and '.quit' immediately terminate the REPL."""
    # Test with '.exit'
    inputs = iter([".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out
    assert "Bye!" in out

    # Test with '.quit'
    inputs = iter([".quit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out
    assert "Bye!" in out


def test_meta_help(monkeypatch, capsys):
    """
    Verify that '.help' displays the list of meta-commands exactly as implemented.
    The help text should include .exit, .quit, .history, !N, .clear, and .reload.
    """
    inputs = iter([".help", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out

    # Check for the main header and at least two known lines
    assert "REPL meta-commands" in out
    assert ".exit" in out
    assert ".history" in out
    assert ".clear" in out
    assert ".reload" in out


def test_meta_history(monkeypatch, capsys):
    """
    Verify that '.history' prints any previously stored lines.
    In this test, we manually add two entries to readline history,
    then invoke '.history' to confirm they appear in output.
    """
    readline.clear_history()
    readline.add_history("alpha")
    readline.add_history("beta")

    inputs = iter([".history", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out

    # After '.history', the two history entries should be listed
    assert "1: alpha" in out
    assert "2: beta" in out


def test_meta_clear(monkeypatch, capsys):
    """
    Verify that '.clear' calls os.system('clear').
    We patch os.system so it simply records the call, without actually clearing screen.
    """
    cleared = []
    monkeypatch.setattr(os, "system", lambda cmd: cleared.append(cmd))

    inputs = iter([".clear", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    repl = GenericREPL(interpreter=DummyInterpreter(), prompt="", hello_sentence="")
    repl.loop()
    out = capsys.readouterr().out

    # os.system('clear') should have been called exactly once
    assert cleared == ["clear"]
    # The REPL should still exit normally after .exit
    assert "Bye!" in out


def test_meta_reload(monkeypatch, capsys, tmp_path):
    """
    Verify that '.reload' re-executes all lines from the init file.
    We create a temporary file with two commands, then check that eval()
    is called on each of them again when '.reload' is used.
    """
    # Prepare a fake init file
    init_file = tmp_path / "commands.txt"
    init_file.write_text("line1\nline2\n")

    # Track which lines are executed
    interpreter = DummyInterpreter()

    # Monkeypatch input() to simulate: ".reload" → ".exit"
    inputs = iter([".reload", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # Instantiate REPL, then assign the init_file path so loop() knows it
    repl = GenericREPL(interpreter=interpreter, prompt="", hello_sentence="")
    repl.init_file = str(init_file)  # nostri inform REPL of the file to reload

    # Before reload, we want to simulate that the REPL already ran the init-file once:
    # replicate how repl() itself would have done (we directly call eval on each init line):
    for cmd in init_file.read_text().splitlines():
        interpreter.eval(cmd)

    # Now run the loop; the first command '.reload' should re-run "line1" and "line2"
    repl.loop()

    # Expect total of 4 eval() calls: 2 from initial pre-loading + 2 from reload
    assert interpreter.executed == ["line1", "line2", "line1", "line2"]


def test_meta_invalid(monkeypatch, capsys):
    """
    Verify that typing an unknown '.meta' command simply invokes interpreter.eval(),
    i.e., it's treated as a regular command, not a REPL meta-command.
    Here, '.foobar' is not recognized as meta, so DummyInterpreter.eval() should receive it.
    """
    inputs = iter([".foobar", ".exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    interpreter = DummyInterpreter()
    repl = GenericREPL(interpreter=interpreter, prompt="", hello_sentence="")
    repl.loop()

    # Since '.foobar' was not a known meta-command, it reaches interpreter.eval()
    assert interpreter.executed == [".foobar"]
