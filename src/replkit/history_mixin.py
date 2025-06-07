# history_mixin.py

import readline


class HistoryMixin:
    """Provides history management for a REPL using readline."""

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

    def add_history_once(self, line: str):
        """Adds a line to readline history if it's not already the last entry."""
        hist_len = readline.get_current_history_length()
        if hist_len == 0 or readline.get_history_item(hist_len) != line:
            readline.add_history(line)
