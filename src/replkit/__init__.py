# replkit/__init__.py
"""
replkit package

This package provides a flexible and reusable REPL (Read-Eval-Print Loop) engine
that can be used to build interactive interpreters for domain-specific languages,
CLI tools, or educational interpreters.

It includes:

GenericREPL: the main REPL loop class with history and completion

REPLCompleter: customizable tab-completion logic

CLI entry point to launch a REPL via replkit script
"""

from .generic_repl import repl, GenericREPL, REPLCompleter

__all__ = ["repl", "GenericREPL", "REPLCompleter"]

__version__ = "0.1.0"
