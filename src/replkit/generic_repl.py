"""
replkit.generic_repl

Provides a generic REPL engine with pluggable interpreters, command history,
tab-completion, alias support and meta-command support.
"""

import os
import readline
import logging
import argparse
import re
from .cli_utils import configure_logger, expand_user_paths


class REPLCompleter:
    """Provides tab-completion for REPL commands using interpreter keywords, meta-commands, aliases, and history."""

    def __init__(self, interpreter, aliases=None, meta_commands=None):
        """Initializes the REPL completer.

        Args:
            interpreter: The interpreter instance providing `get_keywords()`.
            aliases: Optional dictionary of aliases.
            meta_commands: Optional set of built-in REPL commands.
        """
        self.interpreter = interpreter
        self.aliases = aliases or {}
        self.meta_commands = meta_commands or {
            ".exit",
            ".quit",
            ".help",
            ".history",
            ".clear",
            ".reload",
            ".load",
            ".alias",
            ".unalias",
        }
        self.matches = []

    def complete(self, text, state):
        """Returns completion suggestions for the current input.

        Args:
            text: The current input fragment.
            state: The completion index (used by readline).

        Returns:
            A suggested word (str) for autocompletion or None if no match.
        """
        if state == 0:
            words = set(self.meta_commands)

            if hasattr(self.interpreter, "get_keywords"):
                try:
                    words.update(self.interpreter.get_keywords())
                except Exception:
                    pass

            words.update(self.aliases.keys())

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
        aliases_file=".repl_aliases",
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
        self.aliases_file = aliases_file
        self.aliases = {}

    def add_history_once(self, line: str):
        """Adds a line to readline history if it's not already the last entry."""
        hist_len = readline.get_current_history_length()
        if hist_len == 0 or readline.get_history_item(hist_len) != line:
            readline.add_history(line)

    def handle_alias_command(self, line: str) -> bool:
        """Handles alias creation, listing, and removal.

        Args:
            line: A command line starting with .alias or .unalias.

        Returns:
            True if the line was an alias command, False otherwise.
        """
        if line.startswith(".alias"):
            parts = line[len(".alias") :].strip()
            if not parts:
                if not self.aliases:
                    print("No aliases defined.")
                else:
                    for name, expr in sorted(self.aliases.items()):
                        print(f"{name} = {expr}")
            else:
                if "=" not in parts:
                    print("Usage: .alias name=expression")
                    return True
                name, expr = map(str.strip, parts.split("=", 1))
                if not name.startswith("@") or not name[1:].isidentifier():
                    print(
                        f"Invalid alias name: '{name}' (must start with '@' and be a valid identifier)"
                    )
                    return True
                if not expr:
                    print("Alias expression cannot be empty.")
                    return True
                try:
                    expr_expanded = self.expand_aliases(expr)
                except ValueError as e:
                    print(f"Alias error in expression: {e}")
                    return True
                if name in self.aliases:
                    print(
                        f"Alias '{name}' replaced (was: {self.aliases[name]}) → now: {expr_expanded}"
                    )
                else:
                    print(f"Alias added: {name} = {expr_expanded}")
                self.aliases[name] = expr_expanded
            return True
        if line.startswith(".unalias"):
            parts = line[len(".unalias") :].strip()
            if parts in self.aliases:
                del self.aliases[parts]
                print(f"Alias removed: {parts}")
            else:
                print(f"No such alias: {parts}")
            return True
        self.add_history_once(line)

        return False

    def expand_aliases(self, line: str) -> str:
        """Expands all aliases in a given input line.

        Raises:
            ValueError: If an alias used in the line is not defined.
        """
        if not self.aliases or "@" not in line:
            return line

        def tokenize(expr):
            token_pattern = r"""(\".*?\"|\'.*?\'|\w+|@[a-zA-Z_][\w_]*|[^\s])"""
            return re.findall(token_pattern, expr)

        tokens = tokenize(line)
        result = []

        for token in tokens:
            if re.fullmatch(r"@[a-zA-Z_]\w*", token):
                if token in self.aliases:
                    result.append(f"({self.aliases[token]})")
                else:
                    raise ValueError(f"Unknown alias: '{token}'")
            else:
                result.append(token)

        return " ".join(result)

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

    def load_aliases_file(self, filename):
        """Loads alias definitions from a file (lines starting with .alias)."""
        if not os.path.exists(filename):
            self.logger.warning("Aliases file not found: %s", filename)
            return
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(".alias"):
                        self.handle_alias_command(line)
            self.logger.info("Loaded aliases file: %s", self.aliases_file)
        except Exception as e:
            print(f"Error loading aliases file {filename}: {e}")

    def save_aliases_file(self, filename):
        """Saves current aliases to a file using .alias syntax."""
        try:
            with open(filename, "w") as f:
                for name, expr in sorted(self.aliases.items()):
                    f.write(f".alias {name} = {expr}\n")
            self.logger.info("Saved aliases to: %s", self.aliases_file)
        except Exception as e:
            print(f"Error saving aliases to {filename}: {e}")

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
                        if line.startswith("."):
                            if self.handle_alias_command(line):
                                self.add_history_once(line)
                                continue
                            else:
                                print(f"Unknown meta-command in file: {line}")
                                continue
                        try:
                            expanded = self.expand_aliases(line)
                        except ValueError as e:
                            print(f"Alias error in file {path}: {e}")
                            continue
                        self.interpreter.eval(expanded)
                        self.add_history_once(line)
                    except Exception as e:
                        if show_errors:
                            print(f"Error in {label or path}: {e}")
        except Exception as e:
            print(f"Failed to read {label or path}: {e}")

    def process_line(self, line: str) -> bool:
        """Processes a single line of input. Returns True to continue, False to exit.

        Args:
            line: The input line to process.

        Returns:
            bool: True to continue the loop, False to exit.
        """
        line = line.strip()
        if not line:
            return True

        # Recall command from history
        if line.startswith("!"):
            try:
                index = int(line[1:])
                recalled = readline.get_history_item(index)
                if recalled is None:
                    print(f"No command at index {index}")
                    return True
                print(f"# {recalled}")
                readline.remove_history_item(readline.get_current_history_length() - 1)
                self.add_history_once(recalled)
                return self.process_line(recalled)
            except ValueError:
                print("Use !N to recall a command by its index.")
            return True

        # Meta-commands
        if line == ".history":
            self.print_history()
            return True

        if line in (".exit", ".quit"):
            print("Bye!")
            return False

        if line == ".help":
            print("REPL meta-commands:")
            print("  .exit, .quit          Exit the REPL")
            print("  .history              Show command history")
            print("  !N                    Recall command at position N")
            print("  .clear                Clear the screen")
            print("  .reload               Reload the init file")
            print("  .load <file>          Load a batch file")
            print("  .alias [@name=expr]   Define or list aliases")
            print("  .unalias @name        Remove an alias")
            print("  .help                 Show this help message")
            return True

        if line == ".clear":
            os.system("clear")  # or 'cls' on Windows
            return True

        if line == ".reload":
            if self.init_file:
                self.load_file(self.init_file, label=".reload")
            else:
                print("No file was originally loaded to reload.")
            return True

        if line.startswith(".load "):
            filepath = line.split(maxsplit=1)[1]
            self.load_file(filepath, label=f".load {filepath}")
            return True

        if self.handle_alias_command(line):
            return True

        # Evaluate the line
        try:
            expanded = self.expand_aliases(line)
        except ValueError as e:
            print(f"Alias error: {e}")
            return True

        try:
            self.interpreter.eval(expanded)
        except Exception as e:
            print(f"Error: {e}")

        self.add_history_once(line)
        return True

    def loop(self):
        """Starts the interactive REPL loop."""
        # Initialize the loop
        self.init_history()
        self.load_aliases_file(self.aliases_file)
        completer = REPLCompleter(self.interpreter, aliases=self.aliases)
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")  # suppress '@' from delimiters
        readline.set_completer_delims(" \t\n")
        print(self.hello_sentence)
        self.logger.info("REPL session started.")

        # Loop's body
        try:
            while True:
                try:
                    line = input(self.prompt)
                except KeyboardInterrupt:
                    print("\nUse .exit .quit or Ctrl-D to leave.")
                    continue
                except EOFError:
                    print("\nBye!")
                    break

                if not self.process_line(line):
                    break
        finally:
            self.save_history()
            self.save_aliases_file(self.aliases_file)


def parse_repl_args(argv=None):
    """Parses command-line arguments for the REPL CLI.

    Args:
        argv: Optional list of arguments (used for testing or programmatic usage).

    Returns:
        argparse.Namespace: The parsed arguments with expanded paths.
    """
    parser = argparse.ArgumentParser(description="Generic REPL CLI")
    parser.add_argument("--prompt", default=">>> ", help="Prompt text")
    parser.add_argument("--hello", default="Welcome to REPL!", help="Welcome message")
    parser.add_argument(
        "--history", default="~/repl_history", help="Path to history file"
    )
    parser.add_argument("--alias", default="~/repl_aliases", help="Alias file path")
    parser.add_argument("--log", default="~/repl.log", help="Log file path")
    parser.add_argument(
        "--loglevel", default="DEBUG", help="Logging level (DEBUG, INFO, WARNING...)"
    )
    parser.add_argument("--run", help="Command to execute before entering the REPL")
    parser.add_argument("--file", help="File containing commands to execute")

    args = parser.parse_args(argv)

    expand_user_paths(args)

    return args


def repl(interpreter=None, argv=None):
    """Main REPL entry point with CLI support.

    Args:
        interpreter: Optional interpreter instance (must implement .eval(), optionally .get_keywords()).
        argv: Optional list of command-line arguments.
    """

    # Parse argv
    args = parse_repl_args(argv)

    # Configure logger
    logger = configure_logger(args.log, args.loglevel)

    # Use provided interpreter or default fallback
    if interpreter is None:
        from .default_interpreter import DefaultInterpreter

        interpreter = DefaultInterpreter()

    # Instantiates the REPL
    repl_instance = GenericREPL(
        interpreter=interpreter,
        prompt=args.prompt,
        hello_sentence=args.hello,
        history_file=args.history,
        aliases_file=args.alias,
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
