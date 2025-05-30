# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2025-05-30

### Added

- Initial implementation of the `GenericREPL` class for building REPLs with pluggable interpreters.
- History management using `readline`, including:
  - persistent history file
  - command recall via `!N`
  - `history` meta-command
- Tab-completion system (`REPLCompleter`) combining:
  - interpreter-provided keywords
  - meta-commands (`exit`, `quit`, etc.)
  - dynamic words from history
- CLI entry point via `python -m replkit.generic_repl` with configurable options:
  - `--prompt`, `--hello`, `--history`, `--log`
- Logging support with customizable log file and log level.
- Modular structure using `src/` layout with `pyproject.toml` and modern PEP 621 metadata.
- Full test coverage for:
  - REPL execution flow
  - command recall
  - completer behavior
  - CLI help output
- Development tooling:
  - Makefile (`install`, `test`, `lint`, `format`, `check`, `clean`)
  - Optional dependencies (`[dev]`) defined in `pyproject.toml`

---

## [Unreleased]

- Placeholder for future features.
