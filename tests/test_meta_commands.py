import tempfile
import readline
from replkit.generic_repl import GenericREPL


class TraceInterpreter:
    def __init__(self):
        self.executed = []

    def eval(self, line):
        self.executed.append(line)

    def get_keywords(self):
        return {"run", "stop"}


def test_history_and_exit(monkeypatch, capsys):
    # 1. Prepare REPL input lines
    lines = iter(
        [
            "run",  # will be interpreted
            "history",  # triggers REPL history print
            "exit",  # ends the REPL
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: next(lines))

    # 2. Fake empty readline history
    monkeypatch.setattr(readline, "get_current_history_length", lambda: 1)
    monkeypatch.setattr(readline, "get_history_item", lambda i: "run")

    interpreter = TraceInterpreter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        repl = GenericREPL(
            interpreter=interpreter,
            history_file=temp_file.name,
            prompt="",
            hello_sentence="",
        )
        repl.loop()

    # 3. Check outputs
    captured = capsys.readouterr()
    assert "1: run" in captured.out
    assert interpreter.executed == ["run"]


def test_command_recall(monkeypatch, capsys):
    lines = iter(["!1", "exit"])  # recall "run"

    monkeypatch.setattr("builtins.input", lambda _: next(lines))

    # Inject a real command into readline history
    readline.clear_history()
    readline.add_history("run")

    # Adapter readline mock to reflect that
    monkeypatch.setattr(readline, "get_current_history_length", lambda: 1)
    monkeypatch.setattr(
        readline, "get_history_item", lambda i: "run" if i == 1 else None
    )

    interpreter = TraceInterpreter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        repl = GenericREPL(
            interpreter=interpreter,
            history_file=temp_file.name,
            prompt="",
            hello_sentence="",
        )
        repl.loop()

    assert interpreter.executed == ["run"]
