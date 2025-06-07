# replkit Architecture

## Overview

`replkit` is built for modularity and extensibility. Its architecture is based on composable mixins, a modular command strategy, and a fully pluggable interpreter interface.

---

## Key Components

### GenericREPL

The main controller. Composes:

- `HistoryMixin` for command history
- `FileLoaderMixin` for script/init file support
- `AliasMixin` for persistent alias management

### Mixins

Each mixin adds one responsibility:

- **HistoryMixin**: Readline-based command history
- **FileLoaderMixin**: `.load`, `.reload`, batch file loading and startup/init file loading and reloading
- **AliasMixin**: Persistent, validated alias definitions (`@foo`, `.alias`, `.unalias` commands)

### Meta-Commands

- Strategy pattern: each meta-command is a subclass of `BaseCommand`.
- Registered in `command_handlers`.
- To add new commands, subclass `BaseCommand` and add to the list.

### REPLCompleter

- Provides tab-completion for:
  - Interpreter keywords (via `get_keywords()`)
  - Meta-commands
  - Aliases (`@foo`)
  - User history

### Interpreter

- Any Python class with `.eval(line)` (and, optionally, `.get_keywords()`).
- Decoupled: interpreter state and logic are totally independent from the REPL core.

---

## Command flow

```text
User input
   |
   v
[expand_aliases] (AliasMixin)
   |
   +-- if meta-command: [handled by REPLCommands]
   |
   +-- else: [interpreter.eval(line)]
   |
   v
[history tracking]
```

---

## Schéma ASCII d’architecture (à mettre dans ARCHITECTURE.md ou README)

```txt
           ┌────────────────────────┐
           │      GenericREPL       │
           │   (main controller)    │
           └─────────┬──────────────┘
                     │
   ┌─────────────────┼─────────────────┬─────────────────────┐
   │                 │                 │                     │
┌──────┐        ┌────────────┐    ┌───────────────┐     ┌────────────┐
│Interpreter   │HistoryMixin│    │FileLoaderMixin│     │AliasMixin  │
│(your logic)  │            │    │               │     │            │
└──────┘        └────────────┘    └───────────────┘     └────────────┘
   │                 │                 │                     │
   │                 │                 │                     │
   │                 │                 │                     │
   └──────────────┬─────────────────────────────┬────────────┘
                  │                             │
            ┌────────────┐                 ┌─────────────┐
            │REPLCompleter│                 │REPLCommands│
            └────────────┘                 └─────────────┘
                     │                        ▲
          (completion for keywords,           │
           aliases, meta, history)        (meta-command
                                            handlers)
```

**Légende :**

- **GenericREPL** : cœur, compose les mixins et gère la boucle.
- **Mixins** : fonctionnalités indépendantes (history, file, aliases).
- **Interpreter** : injectable, tu mets ce que tu veux (MiniLang, Forth, etc.).
- **REPLCompleter** : suggestions tab.
- **REPLCommands** : stratégie de meta-commandes extensible.

---

## Extending the REPL

**To add a new meta-command:**

- Subclass `BaseCommand` in `repl_commands.py`
- Implement `matches(line)` and `execute(line, repl)`
- Add an instance to `GenericREPL.command_handlers`

**To add a new feature:**

- Implement a mixin (see `history_mixin.py` etc.)
- Compose it in `GenericREPL`

**To add a new interpreter:**

- Write a Python class with `.eval(line)` and (optionally) `.get_keywords()`
- Inject it via the `repl()` function

---

## Testing Policy

- Each mixin/module/command must be tested in isolation (unit tests)
- Integration tests simulate a user session with monkeypatched input
- When you add a new handler or feature, add or update the corresponding test module

---

## File organization

```
src/replkit/
    generic_repl.py
    repl_commands.py
    repl_completer.py
    alias.py
    alias_mixin.py
    file_loader_mixin.py
    history_mixin.py
    cli_utils.py
tests/
    test_generic_repl.py
    test_commands.py
    test_aliases.py
    ...
```

---

## Contact

See [README.md](./README.md) for links and further docs.
