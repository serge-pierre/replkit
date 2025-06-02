"""
replkit.generic_repl

Provides a generic REPL engine with pluggable interpreters, command history,
tab-completion, and meta-command support.
"""

import os
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
        # Default set of .meta-commands
        self.meta_commands = meta_commands or {
            ".exit",
            ".quit",
            ".help",
            ".history",
            ".clear",
            ".reload",
        }
        self.interpreter = interpreter
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
        init_file: (optional) Path to a file whose contents were executed at startup.
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
        self.init_file = None  # Will hold the path to a file executed before looping

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

    def load_file(self, path, *, label=None, show_errors=True):
        """Loads and executes each command from a file.

        Args:
            path (str): The file path.
            label (str): Optional label for messages (e.g. "init file", ".reload", etc).
            show_errors (bool): Whether to print errors from eval.
        """
        if not os.path.exists(path):
            print(f"{label or 'File'} not found: {path}")
            return

        print(f"Loading {label or path}...")

        try:
            with open(path) as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        self.interpreter.eval(line)
                        readline.add_history(line)
                    except Exception as e:
                        if show_errors:
                            print(f"Error in {label or path}: {e}")
        except Exception as e:
            print(f"Failed to read {label or path}: {e}")

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
                except KeyboardInterrupt:
                    # Handle Ctrl-C gracefully
                    print("\nUse .exit .quit or Ctrl-D to leave.")
                    continue
                except EOFError:
                    # Handle Ctrl-D: exit immediately
                    print("\nBye!")
                    break

                if not line:
                    continue

                # Meta-command: !N – recall a previous history entry
                if line.startswith("!"):
                    try:
                        index = int(line[1:])
                        recalled = readline.get_history_item(index)
                        if recalled is None:
                            print(f"No command at index {index}")
                            continue
                        print(f"# {recalled}")
                        line = recalled
                        # Replace the “!N” entry in history with the recalled command
                        readline.remove_history_item(
                            readline.get_current_history_length() - 1
                        )
                        readline.add_history(line)
                    except ValueError:
                        print("Use !N to recall a command by its index.")
                        continue

                # Meta-commands prefixed with '.'
                if line == ".history":
                    self.print_history()
                    continue

                if line in (".exit", ".quit"):
                    print("Bye!")
                    break

                if line == ".help":
                    print("REPL meta-commands:")
                    print("  .exit, .quit     Exit the REPL")
                    print("  .history         Show command history")
                    print("  !N               Recall command at position N")
                    print("  .clear           Clear the screen")
                    print("  .reload          Reload the init file")
                    print("  .help            Show this help message")
                    continue

                if line == ".clear":
                    os.system("clear")  # or 'cls' on Windows
                    continue

                if line == ".reload":
                    if self.init_file:
                        self.load_file(self.init_file, label=".reload")
                    else:
                        print("No file was originally loaded to reload.")
                    continue

                if line.startswith(".load "):
                    filepath = line.split(maxsplit=1)[1]
                    self.load_file(filepath, label=f".load {filepath}")
                    continue

                # Evaluate any other line through the interpreter
                self.interpreter.eval(line)

            # End of while True
        finally:
            self.save_history()


def repl(interpreter=None, argv=None):
    """Main REPL entry point.

    Args:
        interpreter: Interpreter instance implementing .eval() and optionally .get_keywords()
        argv: Optional list of CLI arguments (e.g., ["--log", "out.log"])
    """

    class DefaultInterpreter:
        """Simple interpreter used if no interpreter is passed."""

        def __init__(self):
            self.words = {"print", "dup", "drop", "swap"}

        def eval(self, line):
            print(f"You typed: {line}")

        def get_keywords(self):
            return self.words

    parser = argparse.ArgumentParser(description="Generic REPL runner")

    parser.add_argument(
        "--history", default="~/repl_history", help="Path to history file"
    )
    parser.add_argument("--prompt", default=">>> ", help="Prompt text")
    parser.add_argument("--hello", default="Welcome to REPL!", help="Welcome message")
    parser.add_argument("--log", default="~/repl.log", help="Log file path")
    parser.add_argument(
        "--loglevel", default="DEBUG", help="Logging level (DEBUG, INFO, WARNING...)"
    )
    parser.add_argument("--run", help="Command to execute before entering the REPL")
    parser.add_argument("--file", help="File containing commands to execute")

    args = parser.parse_args(argv)
    args.history = str(Path(args.history).expanduser())
    args.log = str(Path(args.log).expanduser())

    # Configure logger
    logger = logging.getLogger("repl_logger")
    logger.setLevel(getattr(logging, args.loglevel.upper(), logging.DEBUG))

    handler = logging.FileHandler(args.log)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    # Use provided interpreter or default fallback
    if interpreter is None:
        interpreter = DefaultInterpreter()

    repl_instance = GenericREPL(
        interpreter=interpreter,
        history_file=args.history,
        prompt=args.prompt,
        hello_sentence=args.hello,
        logger=logger,
    )

    # Store init_file so .reload can re-execute it
    repl_instance.init_file = args.file

    # Pre-execute commands from --file, if provided
    if args.file:
        repl_instance.init_file = args.file
        repl_instance.load_file(args.file, label="init file", show_errors=False)

    # Pre-execute single command from --run, if provided
    if args.run:
        repl_instance.interpreter.eval(args.run)
        readline.add_history(args.run)

    # Launch interactive loop
    repl_instance.loop()


if __name__ == "__main__":
    repl()
