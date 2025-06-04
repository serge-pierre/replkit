# replkit

`replkit` is a reusable and extensible REPL engine for building custom interactive command-line environments in Python.

It supports interpreter injection, command history, auto-completion, script execution, aliasing, and batch command loading.

---

## Features

- Interactive REPL loop with prompt and welcome message
- Pluggable interpreter (user-defined `eval()` and `get_keywords()`)
- Persistent history (`readline`-based)
- History recall via `!N`
- Alias system:
  - Define aliases using `.alias @name = expression`
  - Expand aliases before evaluation
  - Remove with `.unalias @name`
  - Tab completion support for alias names
  - Aliases are stored/restored across sessions
- Meta-commands:
  - `.exit`, `.quit` — Exit the REPL
  - `.help` — Show built-in REPL commands
  - `.history` — Show command history
  - `.clear` — Clear the screen
  - `.reload` — Re-execute the `--file` passed at startup
  - `.load <file>` — Load and run commands from a file
  - `.alias [@name = expr]` — List aliases or define new alias
  - `.unalias @name` — Delete alias @name
- Batch file support:
  - `--file` for preloading commands at startup
  - `--run` to inject a one-line command
  - Lines starting with `#` and empty lines are ignored
- Tab completion for interpreter keywords, meta-commands, aliases, and history
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

### Development setup

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

### Format, lint, type-check and other command

(Check the Makefile for details)

```bash
make install
make format
make lint
make test
make clean
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
        "--file", "init.txt",
        "--alias", "aliases.txt"
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

## Alias examples

```txt
.alias @dbl = dup +
.alias @square = @dbl *

@dbl 4      # Expands to: (dup +) 4
@square 2   # Expands to: ((dup +) *) 2
.unalias @square
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
| `.alias`          | Show or define aliases                      |
| `.unalias @name`  | Remove a defined alias                      |
| `!N`              | Recall the N-th command in history          |

---

## Example projects

- `math_repl.py` – A math evaluator using Python `eval()`
- `calc_boolean_repl.py` – A boolean calculator REPL (see [docs/interpreter_guide.md](docs/interpreter_guide.md))
- `json_query_repl.py` – Query JSON using a mini DSL

---

## Roadmap ideas

- Support for multi-line command blocks
- Optional typed variables or scoped contexts
- Plug-in support for interpreters via entry-points

---

## License

MIT License

© 2025–present Serge Pierre

---

## Author

Serge Pierre  
[https://github.com/serge-pierre](https://github.com/serge-pierre)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.
