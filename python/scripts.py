#!/usr/bin/env python3
"""Helper scripts for development tasks."""

import subprocess
import sys


def run_command(cmd: str) -> int:
    """Run a shell command and return exit code."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def check() -> None:
    """Run all checks (linting, type checking, tests)."""
    print("=" * 60)
    print("Running all checks...")
    print("=" * 60)

    commands = [
        "poetry run ruff check camino_ai tests",
        "poetry run black --check camino_ai tests",
        "poetry run isort --check-only camino_ai tests",
        "poetry run mypy camino_ai",
        "poetry run pytest --cov=camino_ai --cov-report=term-missing",
    ]

    for cmd in commands:
        exit_code = run_command(cmd)
        if exit_code != 0:
            print(f"\n❌ Command failed: {cmd}")
            sys.exit(exit_code)
        print()

    print("=" * 60)
    print("✅ All checks passed!")
    print("=" * 60)


def format() -> None:
    """Auto-format code."""
    print("=" * 60)
    print("Formatting code...")
    print("=" * 60)

    commands = [
        "poetry run ruff check --fix camino_ai tests",
        "poetry run black camino_ai tests",
        "poetry run isort camino_ai tests",
    ]

    for cmd in commands:
        run_command(cmd)
        print()

    print("=" * 60)
    print("✅ Formatting complete!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check()
        elif sys.argv[1] == "format":
            format()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            sys.exit(1)
    else:
        check()
