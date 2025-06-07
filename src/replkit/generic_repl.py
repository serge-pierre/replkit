"""
replkit.generic_repl

Provides a generic REPL engine with pluggable interpreters, command history,
tab-completion, alias support and meta-command support.
"""

import readline
import logging
import argparse
from .cli_utils import configure_logger, expand_user_paths
from .repl_commands import (
    ExitCommand,
    HelpCommand,
    ClearCommand,
    HistoryCommand,
    ReloadCommand,
    LoadCommand,
    AliasCommand,
    UnaliasCommand,
)
from .alias import expand_aliases
from .history_mixin import HistoryMixin
from .file_loader_mixin import FileLoaderMixin
from .alias_mixin import AliasMixin


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


class GenericREPL(HistoryMixin, FileLoaderMixin, AliasMixin):
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
        self.command_handlers = [
            ExitCommand(),
            HelpCommand(),
            ClearCommand(),
            HistoryCommand(),
            ReloadCommand(),
            LoadCommand(),
            AliasCommand(),
            UnaliasCommand(),
        ]

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
        for cmd in self.command_handlers:
            if cmd.matches(line):
                return cmd.execute(line, self)

        # Evaluate the line
        try:
            expanded_line = expand_aliases(line, self.aliases)
        except ValueError as e:
            print(f"Alias error: {e}")
            return True

        try:
            self.interpreter.eval(expanded_line)
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
