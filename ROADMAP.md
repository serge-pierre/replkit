# REPLKIT — Development Roadmap

This document outlines the key milestones for the `replkit` project, a generic, extensible, modular, and configurable REPL. It aims to structure medium-term development and identify major features per version.

---

## Current Version: `v1.0-aliases`

### Achieved Goals:

- Full alias management:
  - Definition, deletion, strict substitution
  - Automatic persistence in `.repl_aliases`
- History with duplicate protection (`.repl_history`)
- Completion: keywords, commands, aliases
- Up-to-date `.help` command
- Comprehensive unit tests
- Proper interpretation of init files (`--file`) and `.load`

---

## Next Version: `v1.1-meta`

### Goal: Support for **Dynamic Meta-Commands**

Allow injected interpreters to dynamically declare `.name` commands, accessible via `.help`, with automatic completion.

**Tasks:**

- [ ] Add `get_meta_commands()` method to the interpreter
- [ ] Dynamically call handlers from `GenericREPL`
- [ ] Automatic command name completion
- [ ] Dynamic display in `.help`
- [ ] Optional addition of `.describe .cmd`

---

## Version `v1.2-config`

### Goal: **User REPL Profile Management**

Launch independent REPL sessions with profile-specific aliases and history.

**Tasks:**

- [ ] CLI option `--profile NAME`
- [ ] Management of `.repl_history.NAME`, `.repl_aliases.NAME` files
- [ ] Default name: `default`

---

## Version `v1.3-scripted`

### Goal: Support for Scripted REPL Tests

Example `.repl` file format:

```
> .alias @X = A and B
> < Alias added: @X = A and B
> @X or C
> < True
```

**Tasks:**

- [ ] REPL test format
- [ ] Tool `replkit --test tests/test1.repl`
- [ ] Automatic output verification

---

## Version `v1.4-sdk`

### Goal: Provide a Clear API for Integrating New Languages

**Tasks:**

- [ ] `REPLInterpreter` class with `eval()`, `get_meta_commands()`, `get_keywords()` interfaces
- [ ] Example interpreters: MiniLang, Calc, Scheme
- [ ] Integration into `GenericREPL`

---

## Version `v1.5-ui`

### Goal: Visual REPL Interface with `textual` or `rich`

**Tasks:**

- [ ] Styled output (`Alias added`, errors, results)
- [ ] Multi-line input
- [ ] History navigation, tabs, auto-focus

---

## Version `v2.0-multilang`

### Goal: Make `replkit` Multilingual

**Tasks:**

- [ ] Language detection (`--lang python`, `--lang node`)
- [ ] Standard wrappers: `guile`, `node`, `forth`, etc.
- [ ] Error, I/O, and completion standardization

---

## Version Summary

| Version          | Main Feature                          |
| ---------------- | ------------------------------------- |
| `v1.0-aliases`   | Robust alias management, stable REPL  |
| `v1.1-meta`      | Customizable dynamic meta-commands    |
| `v1.2-config`    | Configurable user profiles            |
| `v1.3-scripted`  | Automated REPL scenario execution     |
| `v1.4-sdk`       | Third-party interpreter integration   |
| `v1.5-ui`        | Visual and interactive REPL interface |
| `v2.0-multilang` | Plug-and-play multi-language support  |

---

## Long-Term Goal

Make `replkit` a **universal toolkit for interactive REPLs**—modular, extensible, and embeddable in educational, exploratory, or DSL projects.
