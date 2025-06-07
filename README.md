![Python](https://img.shields.io/badge/python-3.8%2B-blue)
[![License](https://img.shields.io/github/license/serge-pierre/replkit)](./LICENSE)

# replkit

A modular, extensible, interpreter-agnostic REPL toolkit for Python.

---

## Features

- Interactive REPL engine with command history (readline)
- Pluggable interpreter (just provide `.eval()`, `.get_keywords()` optional)
- Extensible meta-command system (`.exit`, `.help`, `.alias`, etc.)
- Alias system with file persistence and tab-completion
- History and aliases saved between sessions
- Easy script file loading/init support
- Complete test suite, robust codebase, ready for extension

---

## Installation

```bash
pip install git+https://github.com/serge-pierre/replkit.git
```

---

## Quick Start

Minimal REPL with your own interpreter:

```python
from replkit import repl

class MyInterpreter:
    def eval(self, line):
        print(f"Eval: {line}")
    def get_keywords(self):
        return {"print", "run", "exit"}

repl(MyInterpreter())
```

---

## CLI usage

```bash
python -m replkit.generic_repl --prompt "MyREPL> " --history ~/.myrepl_history
```

| Option       | Description                           |
| ------------ | ------------------------------------- |
| `--history`  | Path to history file                  |
| `--alias`    | Alias file (`.alias ...`)             |
| `--log`      | Path to log file                      |
| `--loglevel` | Logging level (DEBUG, INFO, etc.)     |
| `--hello`    | Welcome message                       |
| `--prompt`   | Prompt text                           |
| `--run`      | Command to execute before REPL starts |
| `--file`     | File to execute at startup            |

---

## Architecture Overview

- **GenericREPL**: Main controller, composes mixins for modularity.
- **Mixins**: Each core feature (history, aliases, file loading) is isolated in a dedicated mixin for clarity and reusability.
- **Meta-Commands**: Strategy objects; add or override by subclassing `BaseCommand`.
- **REPLCompleter**: Autocompletion for keywords, meta-commands, aliases, history.
- **Interpreter**: Pluggable; must expose `.eval(line)` (and optionally `.get_keywords()` for completion).
- **Tested independently**: Every component comes with its own unit tests.

See [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a detailed breakdown.

---

## How to Extend

- **Add meta-commands**: See `repl_commands.py` and subclass `BaseCommand`.
- **Add new mixins/features**: Implement a mixin class and compose into `GenericREPL`.
- **Write a new interpreter**: Just implement `.eval(line)` and (optionally) `.get_keywords()`.
- **Test your extensions**: Add a new test module, mock as needed.

---

## Documentation

- [User guide: `repl.md`](docs/repl.md)
- [Interpreter API: `interpreter_guide.md`](docs/interpreter_guide.md)
- [Architecture: `ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [Changelog: `CHANGELOG.md`](CHANGELOG.md)

---

## Contributing

PRs and bug reports are welcome! Please add tests for any new feature or bugfix.

---

## License

MIT

© 2025–present Serge Pierre

---

## Author

Serge Pierre  
[https://github.com/serge-pierre](https://github.com/serge-pierre)
