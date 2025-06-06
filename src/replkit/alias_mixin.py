# alias_mixin.py

import os
from replkit.alias import handle_alias_command


class AliasMixin:
    """Provides support for loading and saving alias definitions."""

    def load_aliases_file(self, filename):
        """Loads alias definitions from a file using .alias syntax."""
        if not os.path.exists(filename):
            self.logger.warning("Aliases file not found: %s", filename)
            return
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(".alias"):
                        handle_alias_command(line, self.aliases)
            self.logger.info("Loaded aliases file: %s", filename)
        except Exception as e:
            print(f"Error loading aliases file {filename}: {e}")

    def save_aliases_file(self, filename):
        """Saves current aliases to a file using .alias syntax."""
        try:
            with open(filename, "w") as f:
                for name, expr in sorted(self.aliases.items()):
                    f.write(f".alias {name} = {expr}\n")
            self.logger.info("Saved aliases to: %s", filename)
        except Exception as e:
            print(f"Error saving aliases to {filename}: {e}")
