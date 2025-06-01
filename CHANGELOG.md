# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] – 2025-06-01

### Added

- New `.load <file>` command to execute external batch files from within the REPL.
- Added `.clear` meta-command to clear the terminal screen using `os.system("clear")`.
- Added `.reload` meta-command to re-execute the original `--file` init file.
- Added CLI option `--run` to execute a single command before entering interactive mode.
- Added CLI option `--file` to preload an init file (now also accessible via `.reload`).
- Tab completion now supports meta-commands (`.help`, `.exit`, etc.).
- Comment lines (starting with `#`) and empty lines are skipped in file loading.
- History recall improved: commands like `!3` replace their entry correctly.
- `GenericREPL` now exposes a reusable `load_file()` method shared by `.reload`, `.load`, and `--file`.

### Changed

- All file-based command executions (`--file`, `.reload`, `.load`) now use a unified logic with consistent behavior and error reporting.
- Errors raised by interpreter evaluation are now caught and reported per line (with file context where applicable).
- The REPL now exits gracefully on EOF and keyboard interrupts, and prints user-friendly messages.

### Fixed

- `.reload` previously printed a "not implemented" message; it now functions as expected.
- `.load` used to evaluate only the last line due to indentation bug — now fixed.
- Unit tests for `.meta` commands were missing — now included and fully passing.
- `test_keyboard_interrupt` and `test_eof_exit` now simulate real conditions correctly and avoid infinite loops.

### Development

- Source code reorganized into `src/` layout for modern packaging.
- Makefile targets for `install`, `format`, `lint`, and `test`.
- Switched to `pyproject.toml` for all configuration (no longer using `setup.cfg`).
- Editable installs now use `pip install -e .[dev]` (PEP 660 compliant).
- README now documents full usage, development, and integration of custom interpreters.

---

## [0.1.0] – 2025-05-30

Initial release of `replkit`.

### Features

- Base `GenericREPL` class with pluggable interpreter.
- Support for history file, tab completion, meta-commands, and interpreter interface.
- CLI with `--prompt`, `--hello`, `--log`, `--loglevel`, `--history`.
