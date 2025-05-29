"""
test_cli.py

Test the command-line interface behavior of replkit. Specifically verifies
that running the module with '--help' outputs usage information.
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
