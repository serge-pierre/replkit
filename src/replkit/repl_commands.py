# repl_commands.py

import os
from replkit.alias import handle_alias_command


class BaseCommand:
    """Abstract base class for REPL meta-commands."""

    def matches(self, line: str) -> bool:
        raise NotImplementedError

    def execute(self, line: str, repl) -> bool:
        """Executes the command.

        Returns:
            True to continue the loop, False to exit.
        """
        raise NotImplementedError

    def describe(self) -> str:
        """Returns a short help line for this command."""
        return ""


class ExitCommand(BaseCommand):
    def matches(self, line):
        return line in (".exit", ".quit")

    def execute(self, line, repl):
        print("Bye!")
        return False

    def describe(self):
        return ".exit, .quit          Exit the REPL"


class HelpCommand(BaseCommand):
    def matches(self, line):
        return line == ".help"

    def describe(self):
        return ".help                 Show this help message"

    def execute(self, line, repl):
        print("REPL meta-commands:")
        for cmd in repl.command_handlers:
            desc = cmd.describe()
            if desc:
                print(f"  {desc}")
        return True


class ClearCommand(BaseCommand):
    def matches(self, line):
        return line == ".clear"

    def execute(self, line, repl):
        try:
            os.system("clear")  # or "cls" on Windows
        except Exception as e:
            print(f"Failed to clear screen: {e}")
        return True

    def describe(self):
        return ".clear                Clear the screen"


class HistoryCommand(BaseCommand):
    def matches(self, line):
        return line == ".history"

    def execute(self, line, repl):
        repl.print_history()
        return True

    def describe(self):
        return ".history              Show command history"


class ReloadCommand(BaseCommand):
    def matches(self, line):
        return line == ".reload"

    def execute(self, line, repl):
        if repl.init_file:
            repl.load_file(repl.init_file, label=".reload")
        else:
            print("No file was originally loaded to reload.")
        return True

    def describe(self):
        return ".reload               Reload the init file"


class LoadCommand(BaseCommand):
    def matches(self, line):
        return line.startswith(".load ")

    def execute(self, line, repl):
        _, *parts = line.split(maxsplit=1)
        if not parts:
            print("Usage: .load <file>")
            return True
        filepath = parts[0]
        repl.load_file(filepath, label=f".load {filepath}")
        return True

    def describe(self):
        return ".load <file>          Load a batch file"


class AliasCommand(BaseCommand):
    def matches(self, line):
        return line.startswith(".alias")

    def execute(self, line, repl):
        handled = handle_alias_command(line, repl.aliases)
        if not handled:
            print("Usage: .alias [@name=expr] or .alias to list aliases")
        return True

    def describe(self):
        return ".alias [@name=expr]   Define or list aliases"


class UnaliasCommand(BaseCommand):
    def matches(self, line):
        return line.startswith(".unalias")

    def execute(self, line, repl):
        handled = handle_alias_command(line, repl.aliases)
        if not handled:
            print("Usage: .unalias @name")
        return True

    def describe(self):
        return ".unalias @name        Remove an alias"
