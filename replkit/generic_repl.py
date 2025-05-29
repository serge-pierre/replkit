import readline
import logging
import argparse
from pathlib import Path

class REPLCompleter:
    def __init__(self, interpreter, meta_commands=None):
        self.interpreter = interpreter
        self.meta_commands = meta_commands or {"exit", "quit", "history", "help"}
        self.matches = []

    def complete(self, text, state):
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
    def __init__(self, interpreter, history_file=".repl_history",
                 history_length=1000, hello_sentence="Welcome to the REPL!",
                 prompt=">>> ", logger=None):
        self.interpreter = interpreter
        self.history_file = history_file
        self.history_length = history_length
        self.hello_sentence = hello_sentence
        self.prompt = prompt
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("REPL initialized with prompt: %s", self.prompt)

    def init_history(self):
        try:
            readline.read_history_file(self.history_file)
            self.logger.info("Loaded history file: %s", self.history_file)
        except FileNotFoundError:
            self.logger.warning("History file not found: %s", self.history_file)
        readline.set_history_length(self.history_length)

    def save_history(self):
        readline.write_history_file(self.history_file)
        self.logger.info("Saved history to: %s", self.history_file)

    def print_history(self):
        for i in range(1, readline.get_current_history_length() + 1):
            print(f"{i}: {readline.get_history_item(i)}")

    def loop(self):
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
                            readline.remove_history_item(readline.get_current_history_length() - 1)
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
    parser = argparse.ArgumentParser(description="Generic REPL runner")
    parser.add_argument("--history", default="~/.repl_history", help="Path to history file")
    parser.add_argument("--prompt", default=">>> ", help="Prompt text")
    parser.add_argument("--hello", default="Welcome to REPL!", help="Welcome message")
    parser.add_argument("--log", default="~/repl.log", help="Log file path")
    parser.add_argument("--loglevel", default="DEBUG", help="Logging level (DEBUG, INFO, WARNING...)")

    args = parser.parse_args()
    args.history = str(Path(args.history).expanduser())
    args.log = str(Path(args.log).expanduser())

    logger = logging.getLogger("repl_logger")
    logger.setLevel(getattr(logging, args.loglevel.upper(), logging.DEBUG))

    handler = logging.FileHandler(args.log)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    class DefaultInterpreter:
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
        logger=logger
    )
    repl.loop()


if __name__ == "__main__":
    main()
