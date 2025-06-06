# file_loader_mixin.py

import os
from replkit.alias import expand_aliases, handle_alias_command


class FileLoaderMixin:
    """Provides support for loading and evaluating batch files."""

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
                        # Handle .alias and .unalias directly
                        if handle_alias_command(line, self.aliases):
                            self.add_history_once(line)
                            continue

                        # Expand and evaluate other lines
                        expanded = expand_aliases(line, self.aliases)
                        self.interpreter.eval(expanded)
                        self.add_history_once(line)

                    except Exception as e:
                        if show_errors:
                            print(f"Error in {label or path}: {e}")
        except Exception as e:
            print(f"Failed to read {label or path}: {e}")
