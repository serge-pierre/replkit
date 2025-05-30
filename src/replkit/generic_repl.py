"""
replkit.generic_repl

Provides a generic REPL engine with pluggable interpreters, command history,
tab-completion, and meta-command support.
"""

import readline
import logging
import argparse
from pathlib import Path


class REPLCompleter:
    """Provides tab-completion for REPL commands using interpreter keywords, meta-commands, and history."""

    def __init__(self, interpreter, meta_commands=None):
        """Initializes the REPL completer.

        Args:
            interpreter: The interpreter instance providing `get_keywords()`.
            meta_commands: Optional set of built-in REPL commands.
        """
        self.interpreter = interpreter
        self.meta_commands = meta_commands or {"exit", "quit", "history", "help"}
        self.matches = []

    def complete(self, text, state):
        """Returns completion suggestions for the current input.

        Args:
            text: The current input fragment.
            state: The completion index (used by readline).

        Returns:
            A suggested word or None.
        """
        if state == 0:
            words = set(self.meta_commands)

            if hasattr(self.interpreter, "get_keywords"):
                try:
                    words.update(self.interpreter.get_keywords())
                except Exception:
                    pass

            for i in range(1, readline.get_current_history_length() + 1):
                entry = readline.get_history_item(i)
                if entry:
                    words.update(entry.strip().split())

            self.matches = sorted(w for w in words if w.startswith(text))

        return self.matches[state] if state < len(self.matches) else None


class GenericREPL:
    """A customizable Read-Eval-Print Loop (REPL) for command interpreters.

    Attributes:
        interpreter: An object with `eval()` method and optional `get_keywords()`.
        history_file: Path to the history file.
        history_length: Maximum number of lines to store in history.
        hello_sentence: Welcome message shown on REPL start.
        prompt: String shown before each input.
        logger: Logger instance for diagnostics.
    """

    def __init__(
        self,
        interpreter,
        history_file=".repl_history",
        history_length=1000,
        hello_sentence="Welcome to the REPL!",
        prompt=">>> ",
        logger=None,
    ):
        """Initializes the REPL environment.

        Args:
            interpreter: The interpreter object.
            history_file: Path to the history file.
            history_length: Max lines to store.
            hello_sentence: Welcome message.
            prompt: Prompt string.
            logger: Logger instance (optional).
        """
        self.interpreter = interpreter
        self.history_file = history_file
        self.history_length = history_length
        self.hello_sentence = hello_sentence
        self.prompt = prompt
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("REPL initialized with prompt: %s", self.prompt)

    def init_history(self):
        """Initializes the readline history from file."""
        try:
            readline.read_history_file(self.history_file)
            self.logger.info("Loaded history file: %s", self.history_file)
        except FileNotFoundError:
            self.logger.warning("History file not found: %s", self.history_file)
        readline.set_history_length(self.history_length)

    def save_history(self):
        """Saves the readline history to file."""
        readline.write_history_file(self.history_file)
        self.logger.info("Saved history to: %s", self.history_file)

    def print_history(self):
        """Prints the current command history to stdout."""
        for i in range(1, readline.get_current_history_length() + 1):
            print(f"{i}: {readline.get_history_item(i)}")

    def loop(self):
        """Starts the interactive REPL loop."""
        self.init_history()
        readline.set_completer(REPLCompleter(self.interpreter).complete)
        readline.parse_and_bind("tab: complete")
        print(self.hello_sentence)
        self.logger.info("REPL session started.")

        try:
            while True:
                try:
                    line = input(self.prompt).strip()
                    self.logger.debug("User input: %s", line)
                    if not line:
                        continue

                    if line.startswith("!"):
                        try:
                            index = int(line[1:])
                            recalled = readline.get_history_item(index)
                            if recalled is None:
                                print(f"No command at index {index}")
                                continue
                            print(f"# {recalled}")
                            line = recalled
                            readline.remove_history_item(
                                readline.get_current_history_length() - 1
                            )
                            readline.add_history(line)
                        except ValueError:
                            print("Use !N to recall a command by its index.")
                            continue

                    if line == "history":
                        self.print_history()
                        continue

                    if line in ("exit", "quit"):
                        raise EOFError()

                    self.interpreter.eval(line)

                except KeyboardInterrupt:
                    print("\nUse Ctrl-D, quit or exit to leave.")
                    continue
                except EOFError:
                    print("\nBye!")
                    break
        finally:
            self.save_history()


def main():
    """Entry point for the command-line REPL."""
    parser = argparse.ArgumentParser(description="Generic REPL runner")
    parser.add_argument(
        "--history", default="~/.repl_history", help="Path to history file"
    )
    parser.add_argument("--prompt", default=">>> ", help="Prompt text")
    parser.add_argument("--hello", default="Welcome to REPL!", help="Welcome message")
    parser.add_argument("--log", default="~/repl.log", help="Log file path")
    parser.add_argument(
        "--loglevel", default="DEBUG", help="Logging level (DEBUG, INFO, WARNING...)"
    )
    parser.add_argument("--run", help="Command to execute before entering the REPL")
    parser.add_argument("--file", help="File containing commands to execute")


    args = parser.parse_args()
    args.history = str(Path(args.history).expanduser())
    args.log = str(Path(args.log).expanduser())

    logger = logging.getLogger("repl_logger")
    logger.setLevel(getattr(logging, args.loglevel.upper(), logging.DEBUG))

    handler = logging.FileHandler(args.log)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    class DefaultInterpreter:
        """Simple interpreter used if no interpreter is passed."""

        def __init__(self):
            self.words = {"print", "dup", "drop", "swap"}

        def eval(self, line):
            print(f"You typed: {line}")

        def get_keywords(self):
            return self.words

    repl = GenericREPL(
        interpreter=DefaultInterpreter(),
        history_file=args.history,
        hello_sentence=args.hello,
        prompt=args.prompt,
        logger=logger,
    )

    if args.file:
        with open(args.file) as f:
            for line in f:
                line = line.strip()
                if line:
                    repl.interpreter.eval(line)

    if args.run:
        repl.interpreter.eval(args.run)

        repl.loop()

if __name__ == "__main__":
    main()
