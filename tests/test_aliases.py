# tests/test_alias.py

import pytest
from replkit.alias import expand_aliases, handle_alias_command


def test_expand_aliases_basic():
    aliases = {
        "@X": "1 2 +",
        "@Y": "3 @X *"
    }
    line = "@Y 4 -"
    expanded = expand_aliases(line, aliases)
    assert expanded == "(3 @X *) 4 -"  # current non-recursive behavior


def test_expand_aliases_unknown_alias():
    aliases = {"@A": "42"}
    with pytest.raises(ValueError, match="Unknown alias: '@B'"):
        expand_aliases("@A @B +", aliases)


def test_handle_alias_definition_adds_entry():
    aliases = {}
    result = handle_alias_command(".alias @sum=1 2 +", aliases)
    assert result is True
    assert "@sum" in aliases
    assert aliases["@sum"] == "1 2 +"  # no parentheses added


def test_handle_alias_redefinition():
    aliases = {"@dup": "x x"}
    result = handle_alias_command(".alias @dup=y y", aliases)
    assert result is True
    assert aliases["@dup"] == "y y"  # no parentheses added


def test_handle_alias_list_output(capsys):
    aliases = {"@a": "1", "@b": "2"}
    handle_alias_command(".alias", aliases)
    out = capsys.readouterr().out
    assert "@a = 1" in out
    assert "@b = 2" in out


def test_handle_alias_invalid_name(capsys):
    aliases = {}
    handle_alias_command(".alias invalid=1", aliases)
    out = capsys.readouterr().out
    assert "Invalid alias name" in out


def test_handle_unalias_success(capsys):
    aliases = {"@foo": "bar"}
    result = handle_alias_command(".unalias @foo", aliases)
    assert result is True
    assert "@foo" not in aliases
    out = capsys.readouterr().out
    assert "Alias removed: @foo" in out


def test_handle_unalias_missing(capsys):
    aliases = {}
    result = handle_alias_command(".unalias @missing", aliases)
    assert result is True
    out = capsys.readouterr().out
    assert "No such alias: @missing" in out

def test_handle_alias_collision(capsys):
    aliases = {"@foo": "old"}
    handle_alias_command(".alias @foo=new", aliases)
    assert aliases["@foo"] == "new"
    out = capsys.readouterr().out
    assert "replaced" in out or "Alias added" in out

def test_handle_alias_special_chars(capsys):
    aliases = {}
    handle_alias_command('.alias @weird="a + b - c"', aliases)
    assert aliases["@weird"] == '"a + b - c"'

def test_expand_aliases_with_nested_alias():
    aliases = {"@A": "1", "@B": "@A 2 +"}
    expanded = expand_aliases("@B", aliases)
    # Selon la sémantique choisie, ajuster ce test si expansion récursive un jour souhaitée
    assert expanded == "(@A 2 +)"  # ou "1 2 +" si expansion récursive
