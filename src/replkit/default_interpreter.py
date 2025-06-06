class DefaultInterpreter:
    """Simple interpreter used if no interpreter is passed."""

    def __init__(self):
        self.words = {"print", "dup", "drop", "swap"}

    def eval(self, line):
        print(f"You typed: {line}")

    def get_keywords(self):
        return self.words
