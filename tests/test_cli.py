"""
test_cli.py

Tests the command-line interface behavior of replkit.generic_repl.
This includes usage help output and simple execution via subprocess.
"""

import subprocess


def test_replkit_cli_help():
    """Ensure 'python -m replkit.generic_repl --help' shows usage text."""
    result = subprocess.run(
        ["python", "-m", "replkit.generic_repl", "--help"],
        capture_output=True,
        text=True,
    )
    assert "usage" in result.stdout.lower()
    assert "--prompt" in result.stdout
    assert "--file" in result.stdout
    assert "--run" in result.stdout


def test_replkit_cli_run_command(tmp_path):
    """Test '--run' option by checking that a command is processed without REPL loop."""
    log_file = tmp_path / "test_run.log"

    # Create a temporary script file to run
    result = subprocess.run(
        [
            "python",
            "-m",
            "replkit.generic_repl",
            "--run",
            "print('Hello from --run')",
            "--log",
            str(log_file),
        ],
        capture_output=True,
        text=True,
    )

    assert "Hello from --run" in result.stdout
    assert "Bye!" in result.stdout


def test_replkit_cli_file_execution(tmp_path):
    """Test '--file' option by feeding a file with a command."""
    test_script = tmp_path / "init.txt"
    test_script.write_text("print('From file')\n")

    result = subprocess.run(
        [
            "python",
            "-m",
            "replkit.generic_repl",
            "--file",
            str(test_script),
            "--run",
            "print('Inline command')",
        ],
        capture_output=True,
        text=True,
    )

    assert "From file" in result.stdout
    assert "Inline command" in result.stdout


def test_cli_alias_file_usage(tmp_path):
    alias_file = tmp_path / "aliases.txt"
    alias_file.write_text(".alias @foo=bar\n")
    result = subprocess.run(
        [
            "python",
            "-m",
            "replkit.generic_repl",
            "--alias",
            str(alias_file),
            "--run",
            "@foo",
        ],
        capture_output=True,
        text=True,
    )
    assert "bar" in result.stdout
