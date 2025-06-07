### `replkit.generic_repl` — A customizable generic REPL

**An extensible REPL engine with support for history, completion, aliasing, and initialization files.**

---

## Class `GenericREPL`

### Constructor

```python
GenericREPL(
    interpreter,
    history_file=".repl_history",
    history_length=1000,
    aliases_file=".repl_aliases",
    hello_sentence="Welcome to the REPL!",
    prompt=">>> ",
    logger=None
)
```

### Key Attributes

- `interpreter`: Instance implementing `.eval()` and optionally `.get_keywords()`
- `history_file`: History file path for `readline`
- `aliases_file`: File with `.alias` definitions
- `prompt`: Prompt string shown before each input
- `logger`: Configured Python logger instance

---

## Key Methods

### `loop()`

Starts the interactive REPL loop.

### `expand_aliases(line)`

Expands aliases in the input line (e.g., `@foo` becomes its full expression). Raises a `ValueError` if an alias is undefined.

Note: This method is now implemented as mixins (e.g. `AliasMixin`) and may not appear directly on `GenericREPL`. Access it via the composed REPL instance.

### `handle_alias_command(line)`

Handles `.alias`, `.unalias`, and their display. Returns `True` if it was a recognized meta-command, `False` otherwise.

Note: This method is now implemented as mixins (e.g. `AliasMixin`) and may not appear directly on `GenericREPL`. Access it via the composed REPL instance.

### `load_file(path, label=None, show_errors=True)`

Executes the contents of a file line by line (processing both commands and aliases).

### `print_history()`, `init_history()`, `save_history()`

Manage the command history using `readline`.

### `load_aliases_file(path)`, `save_aliases_file(path)`

Load or persist aliases from/to a file.

---

## Modular Architecture Note

Starting from v2.0.0, core features like alias handling, file loading, and history management are implemented as modular mixins.
For example, `expand_aliases` and `handle_alias_command` are now provided by the `AliasMixin` and not directly by `GenericREPL`.
This allows for easier extension, independent testing, and clearer code organization.
See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

---

## Other Classes

### `REPLCompleter`

Provides tab-completion for `readline`, including:

- Interpreter keywords
- Meta-commands like `.alias`, `.exit`, etc.
- Defined alias names
- Entries from user history

---

## CLI Entry Point: `repl()`

```bash
python generic_repl.py --history ~/.hist --alias ~/.aliases --log repl.log
```

### Supported Options

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

## Aliases (`@name`)

- `@` prefix is mandatory (e.g., `@double = dup +`)
- Automatic substitution before `eval()`
- Safety: only valid names accepted, clear error handling
- Tab completion supported
- Alias definitions persist via `.alias` file

---

## Extending Meta-Commands

You can add new meta-commands by subclassing `BaseCommand` and adding your handler to the `command_handlers` list of your REPL instance.
See [interpreter_guide.md](./interpreter_guide.md) for a complete example.

---

## Minimal Example

```python
from replkit.generic_repl import repl

class MyInterpreter:
    def eval(self, line):
        print(f"Eval: {line}")
    def get_keywords(self):
        return {"print", "run", "exit"}

repl(MyInterpreter())
```
