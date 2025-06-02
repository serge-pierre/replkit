# replkit

`replkit` is a reusable and extensible REPL engine for building custom interactive command-line environments in Python.

It supports interpreter injection, command history, auto-completion, script execution, and batch command loading.

---

## Features

- Interactive REPL loop with prompt and welcome message
- Pluggable interpreter (user-defined `eval()` and `get_keywords()`)
- Persistent history (`readline`-based)
- History recall via `!N`
- Meta-commands:
  - `.exit`, `.quit` — Exit the REPL
  - `.help` — Show built-in REPL commands
  - `.history` — Show command history
  - `.clear` — Clear the screen
  - `.reload` — Re-execute the `--file` passed at startup
  - `.load <file>` — Load and run commands from a file
- Batch file support:
  - `--file` for preloading commands at startup
  - `--run` to inject a one-line command
  - Lines starting with `#` and empty lines are ignored
- Tab completion for interpreter keywords, meta-commands, and recent history
- Logging support via `--log` and `--loglevel`

---

## Installation

### Production usage

```bash
pip install git+https://github.com/serge-pierre/replkit.git
```

Or clone manually:

```bash
git clone https://github.com/serge-pierre/replkit.git
cd replkit
python -m venv venv
source venv/bin/activate
pip install .
```

Then run:

```bash
python -m replkit.generic_repl
```

---

## Development setup

```bash
git clone https://github.com/serge-pierre/replkit.git
cd replkit
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools
pip install -e .[dev]
```

### Run the tests

```bash
pytest
```

### Format, lint, and type-check

```bash
make format
make lint
make test
```

---

## Usage

### Basic example with default interpreter

```bash
python -m replkit.generic_repl --prompt ">>> " --hello "Welcome!" --log repl.log
```

### With an injected interpreter

Create a Python script, e.g. `math_repl.py`:

```python
from replkit import repl

class MathInterpreter:
    def eval(self, line):
        try:
            result = eval(line)
            print(result)
        except Exception as e:
            print(f"Error: {e}")

    def get_keywords(self):
        return {"+", "-", "*", "/", "(", ")"}

if __name__ == "__main__":
    repl(interpreter=MathInterpreter(), argv=[
        "--prompt", "Math> ",
        "--hello", "Welcome in MathInterpreter!",
        "--file", "init.txt"
    ])
```

Then run:

```bash
python math_repl.py
```

---

## File-based command injection

You can create an init file like `init.txt`:

```txt
# Initialize the session
1 + 2
(5 * 4) / 2

# This line is ignored:
# print("Hello")
```

And load it with:

```bash
python -m replkit.generic_repl --file init.txt
```

Or in an active REPL session:

```txt
Math> .load load.txt
Math> .reload
```

---

## Meta-commands reference

| Command           | Description                                 |
| ----------------- | ------------------------------------------- |
| `.exit` / `.quit` | Exit the REPL                               |
| `.help`           | Show list of REPL meta-commands             |
| `.history`        | Show previously entered commands            |
| `.clear`          | Clear the terminal screen                   |
| `.reload`         | Reload the file passed via `--file`         |
| `.load <file>`    | Load and execute commands from another file |
| `!N`              | Recall the N-th command in history          |

---

## Example projects

- `math_repl.py` – A math evaluator using Python `eval()`
- `calc_boolean_repl.py` – (see [docs/interpreter_guide.md](docs/interpreter_guide.md)) A boolean calculator REPL
- `json_query_repl.py` – Query JSON using a mini DSL

---

## Roadmap ideas

- Add support for multi-line command blocks
- Optional typed variables or context management
- Load interpreters from entry-points or plug-ins
- Management of alias definition

---

## License

MIT License

Copyright (c) 2025-present Serge Pierre

---

## Author

Serge Pierre
[https://github.com/serge-pierre](https://github.com/serge-pierre)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.
