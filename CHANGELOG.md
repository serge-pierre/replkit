# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.0.0] - 2025-06-07

### Added

- Modular architecture using mixins: `HistoryMixin`, `FileLoaderMixin`, `AliasMixin`
- Meta-commands now implemented as extensible strategy objects (subclass `BaseCommand`)
- Alias system: persistent, validated, with tab completion, listing, and removal
- Flexible CLI: history, alias, log, prompt, hello sentence, interpreter, file, and run command
- Full unit and integration test suite for each component and feature
- Documentation: user guide, interpreter API, architecture overview

### Changed

- Refactored core into separate, focused modules for maintainability
- Test coverage increased and simplified
- Error handling improved across all file, alias, and command operations
- CLI and REPL logic now completely decoupled from the interpreter

### Fixed

- Robust file I/O, cross-platform compatibility (history, clear screen, paths)
- Consistent alias expansion, handling of edge cases and user errors

---

## [1.0.0] – 2025-06-06

### Added

- Full alias system with support for:
  - `.alias @NAME = EXPRESSION` to define symbolic aliases
  - `.unalias @NAME` to remove existing aliases
  - Persistent storage of aliases via `.repl_aliases` (loaded and saved automatically)
  - Strict substitution with error reporting on undefined aliases
- Inline alias expansion (`@name`) with safe substitution in interpreter input
- Alias completion: `@...` names are now included in tab-completion
- `.alias` command with no arguments lists all active aliases
- Aliases now persist across REPL sessions, like history
- Aliases are expanded within `.load`, `--file`, and `--run` sources
- History tracking improved to avoid duplicate entries (e.g., with `@X` or `!N`)
- Unit test coverage for:
  - Alias substitution and protection
  - Error handling for undefined and malformed aliases
  - History interaction with `.alias`, `.unalias`, `.load`, and `!N`

### Changed

- `.load` now supports alias definitions in input files (`.alias @X = ...`)
- The REPL no longer crashes if an alias is undefined; instead, a clear `Alias error: ...` is shown
- `.help` and tab completion dynamically reflect current alias list
- Alias definitions in `.alias` now expand other aliases during assignment (e.g., `.alias @X = @Y or Z`)
- Tab completion now unified across aliases, meta-commands, and interpreter keywords

### Fixed

- Commands from `.load` or `--file` were not tracked in history — now correctly logged
- Previously, repeating the same input (e.g., `@Z`) added duplicate entries — now deduplicated
- Alias references like `@A1` are no longer partially expanded (e.g., `(True)1`)
- Fixed inconsistent behavior when `.alias` was used within init files or scripts

### Development

- Added full alias checklist covering edge cases, substitutions, and persistence
- `GenericREPL` cleaned and documented: inline comments clarified for core REPL logic
- Alias handling centralized and unit-tested (`expand_aliases`, `handle_alias_command`)
- Finalized and documented `add_history_once()` method to protect REPL history integrity

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
