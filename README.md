# replkit

`replkit` is a generic REPL engine for building interactive command-line environments with pluggable interpreters.

## Features

- Persistent command history
- Command recall using `!N`
- Auto-completion for meta-commands and interpreter keywords
- Pluggable interpreter class
- Configurable logging
- Argument parsing via CLI

## Installation

We recommend using a Python virtual environment.

### Development mode (editable install)

This is the preferred setup for developers who want to modify and test the project locally.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Upgrade pip and setuptools
pip install --upgrade pip setuptools

# 3. Install the package in editable mode with development dependencies
pip install -e .[dev]

# 4. Run tests to validate installation
pytest
```

This allows you to run and test `replkit` directly from the source code, and use developer tools like `ruff`, `black`, and `pytest`.

You can then run the REPL with:

```bash
replkit --prompt "mlang> " --hello "Welcome to MiniLang!"
```

**Note:** This project uses the `src/` layout. All source code lives in `src/replkit`, and you must run tests from the project root.

### Production install

This is suitable for users who only want to use the tool, not modify it.

```bash
# Install replkit with pip (from local source or GitHub)
pip install .
# Or from GitHub (public repository)
pip install git+https://github.com/yourname/replkit.git
```

This will install the `replkit` CLI command without dev tools.

### Uninstall

```bash
pip uninstall replkit
```
