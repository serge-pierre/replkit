# alias.py

import re


def tokenize(expr):
    """Splits an expression into tokens, preserving quoted strings and aliases."""
    token_pattern = r"""(\".*?\"|\'.*?\'|\w+|@[a-zA-Z_][\w_]*|[^\s])"""
    return re.findall(token_pattern, expr)


def expand_aliases(line: str, aliases: dict) -> str:
    """Expands all aliases in the line using the provided alias dictionary.

    Args:
        line: Input string potentially containing aliases.
        aliases: Dictionary of alias definitions.

    Returns:
        The expanded string.

    Raises:
        ValueError: If a used alias is undefined.
    """
    if not aliases or "@" not in line:
        return line

    tokens = tokenize(line)
    result = []

    for token in tokens:
        if re.fullmatch(r"@[a-zA-Z_]\w*", token):
            if token in aliases:
                result.append(f"({aliases[token]})")
            else:
                raise ValueError(f"Unknown alias: '{token}'")
        else:
            result.append(token)

    return " ".join(result)


def handle_alias_command(line: str, aliases: dict) -> bool:
    """Handles alias and unalias commands on a shared alias dictionary.

    Returns:
        True if handled, False otherwise.
    """
    if line.startswith(".alias"):
        parts = line[len(".alias"):].strip()
        if not parts:
            if not aliases:
                print("No aliases defined.")
            else:
                for name, expr in sorted(aliases.items()):
                    print(f"{name} = {expr}")
        else:
            if "=" not in parts:
                print("Usage: .alias name=expression")
                return True
            name, expr = map(str.strip, parts.split("=", 1))
            if not name.startswith("@") or not name[1:].isidentifier():
                print(f"Invalid alias name: '{name}' (must start with '@' and be a valid identifier)")
                return True
            if not expr:
                print("Alias expression cannot be empty.")
                return True
            try:
                expr_expanded = expand_aliases(expr, aliases)
            except ValueError as e:
                print(f"Alias error in expression: {e}")
                return True
            if name in aliases:
                print(f"Alias '{name}' replaced (was: {aliases[name]}) → now: {expr_expanded}")
            else:
                print(f"Alias added: {name} = {expr_expanded}")
            aliases[name] = expr_expanded
        return True

    if line.startswith(".unalias"):
        parts = line[len(".unalias"):].strip()
        if parts in aliases:
            del aliases[parts]
            print(f"Alias removed: {parts}")
        else:
            print(f"No such alias: {parts}")
        return True

    return False
