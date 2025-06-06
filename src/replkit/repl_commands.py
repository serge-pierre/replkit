# repl_commands.py

import os


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


class ExitCommand(BaseCommand):
    def matches(self, line):
        return line in (".exit", ".quit")

    def execute(self, line, repl):
        print("Bye!")
        return False


class HelpCommand(BaseCommand):
    def matches(self, line):
        return line == ".help"

    def execute(self, line, repl):
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


class ClearCommand(BaseCommand):
    def matches(self, line):
        return line == ".clear"

    def execute(self, line, repl):
        os.system("clear")  # or "cls" on Windows
        return True


class HistoryCommand(BaseCommand):
    def matches(self, line):
        return line == ".history"

    def execute(self, line, repl):
        repl.print_history()
        return True


class ReloadCommand(BaseCommand):
    def matches(self, line):
        return line == ".reload"

    def execute(self, line, repl):
        if repl.init_file:
            repl.load_file(repl.init_file, label=".reload")
        else:
            print("No file was originally loaded to reload.")
        return True


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


class AliasCommand(BaseCommand):
    def matches(self, line):
        return line.startswith(".alias") or line.startswith(".unalias")

    def execute(self, line, repl):
        handled = repl.handle_alias_command(line)
        if not handled:
            print(f"Invalid alias command: {line}")
        return True
