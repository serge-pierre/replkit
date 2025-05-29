import subprocess

def test_replkit_cli_help():
    result = subprocess.run(
        ["python", "-m", "replkit.generic_repl", "--help"],
        capture_output=True,
        text=True
    )
    assert "usage" in result.stdout.lower()
    