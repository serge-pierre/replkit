# REPLKit — Technical Checklist for the Alias System (`@name`)

This checklist aims to validate the robustness, consistency, and usability of the alias system in `replkit`.

---

## 1. Basic Functionality

- [x] `.alias @name = expr` creates an alias
- [x] `.alias` lists all defined aliases
- [x] `.unalias @name` removes an alias
- [x] Expansion takes place before `eval()`
- [x] Expansion does not crash the REPL (errors are handled gracefully)
- [x] The `@` prefix is required (avoids collisions)
- [x] Aliases are included in tab-completion
- [x] `.alias`/`.unalias` commands are added to history

---

## 2. Safety and Consistency

- [x] Invalid alias names are rejected (`@1abc`, `@with space`, etc.)
- [x] Clear error message when using an undefined alias (`Alias error: Unknown alias`)
- [x] Warning or replacement message when redefining an existing alias
- [x] Empty expressions are disallowed: `.alias @foo = `
- [ ] Warning if alias expression is identical to its name (`@foo = @foo`)
- [ ] Future detection of circular definitions (`@A = @B`, `@B = @A`) — not required for v1

---

## 3. UX / Interface

- [x] Tab completion on `@name` works (`readline.set_completer_delims`)
- [x] `.help` lists `.alias`, `.unalias` commands
- [x] Message shown when redefining an alias (`Alias '@x' replaced (was: ...)`)

---

## 4. Integration and Extensibility

- [x] Prepared for future interface for alias persistence
- [x] Validated behavior in scripts (`--file`, `.load`):
- [x] Aliases defined in files are correctly interpreted
- [x] Errors are raised on invalid aliases in files
- [x] Tested compatibility with history recall (`!N`) for alias-containing lines

---

## 5. Recommended Tests

Create unit tests for:

- [x] `expand_aliases()` with multiple alias substitutions
- [x] Detection of unknown alias
- [ ] Alias redefinition
- [ ] Alias removal
- [x] Ensure alias names are never replaced inside longer names (e.g. `@and` ≠ `@andromede`)
