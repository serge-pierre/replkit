# tests/test_commands.py

import pytest
from replkit.repl_commands import (
    ExitCommand, HelpCommand, ClearCommand,
    HistoryCommand, ReloadCommand, LoadCommand,
    AliasCommand, UnaliasCommand,
)
from replkit.alias import handle_alias_command


class DummyREPL:
    def __init__(self):
        self.output = []
        self.init_file = None
        self.loaded = []
        self.aliases = {}
        self.history_printed = False

    def load_file(self, path, label=None, show_errors=True):
        self.loaded.append((path, label))

    def print_history(self):
        self.history_printed = True


def test_exit_command(capsys):
    cmd = ExitCommand()
    assert cmd.matches(".exit")
    assert cmd.matches(".quit")
    assert not cmd.matches(".other")

    dummy = DummyREPL()
    result = cmd.execute(".exit", dummy)
    assert result is False
    assert "Bye!" in capsys.readouterr().out


def test_help_command(capsys):
    dummy = DummyREPL()
    dummy.command_handlers = [ExitCommand(), HelpCommand()]
    cmd = HelpCommand()

    assert cmd.matches(".help")
    assert cmd.execute(".help", dummy) is True
    out = capsys.readouterr().out
    assert "REPL meta-commands:" in out
    assert ".exit" in out


def test_clear_command(monkeypatch):
    called = {}

    def fake_clear(cmd):
        called["cmd"] = cmd

    monkeypatch.setattr("os.system", fake_clear)
    cmd = ClearCommand()
    result = cmd.execute(".clear", DummyREPL())
    assert result is True
    assert called["cmd"] == "clear"


def test_history_command():
    dummy = DummyREPL()
    cmd = HistoryCommand()
    result = cmd.execute(".history", dummy)
    assert result is True
    assert dummy.history_printed


def test_reload_command():
    dummy = DummyREPL()
    dummy.init_file = "init.mlang"
    cmd = ReloadCommand()
    result = cmd.execute(".reload", dummy)
    assert result is True
    assert dummy.loaded == [("init.mlang", ".reload")]


def test_reload_without_file(capsys):
    dummy = DummyREPL()
    cmd = ReloadCommand()
    result = cmd.execute(".reload", dummy)
    assert result is True
    out = capsys.readouterr().out
    assert "No file was originally loaded" in out


def test_load_command():
    dummy = DummyREPL()
    cmd = LoadCommand()
    result = cmd.execute(".load file.mlang", dummy)
    assert result is True
    assert dummy.loaded == [("file.mlang", ".load file.mlang")]


def test_load_command_missing_arg(capsys):
    dummy = DummyREPL()
    cmd = LoadCommand()
    result = cmd.execute(".load", dummy)
    assert result is True
    out = capsys.readouterr().out
    assert "Usage: .load <file>" in out


def test_alias_command_add(capsys):
    dummy = DummyREPL()
    cmd = AliasCommand()
    result = cmd.execute(".alias @t=hello", dummy)
    assert result is True
    assert "@t" in dummy.aliases
    assert dummy.aliases["@t"] == "hello"


def test_alias_command_list(capsys):
    dummy = DummyREPL()
    dummy.aliases = {"@x": "1", "@y": "2"}
    cmd = AliasCommand()
    result = cmd.execute(".alias", dummy)
    assert result is True
    out = capsys.readouterr().out
    assert "@x = 1" in out
    assert "@y = 2" in out


def test_unalias_command(capsys):
    dummy = DummyREPL()
    dummy.aliases["@foo"] = "bar"
    cmd = UnaliasCommand()
    result = cmd.execute(".unalias @foo", dummy)
    assert result is True
    assert "@foo" not in dummy.aliases
    out = capsys.readouterr().out
    assert "Alias removed" in out


def test_clear_command_exception(monkeypatch):
    def fail_clear(cmd):
        raise OSError("fail!")
    monkeypatch.setattr("os.system", fail_clear)
    cmd = ClearCommand()
    # Le REPL ne doit pas crasher sur l’exception !
    try:
        cmd.execute(".clear", DummyREPL())
    except Exception:
        pytest.fail("ClearCommand should handle exceptions in os.system")

def test_command_handlers_extensible():
    class FooCommand:
        def matches(self, line): return line == ".foo"
        def execute(self, line, repl): repl.output.append("foo"); return True
        def describe(self): return ".foo   Custom test command"
    dummy = DummyREPL()
    dummy.command_handlers = [FooCommand()]
    for cmd in dummy.command_handlers:
        if cmd.matches(".foo"):
            assert cmd.execute(".foo", dummy) is True
    assert "foo" in dummy.output
