"""Oracle CLI Examples - Demonstrating production CLI usage.

Examples showing how to use the flext-oracle CLI commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from flext_core import FlextUtilities

# Constants for CLI examples
MAX_OUTPUT_LINES = 3


def _get_cli_examples() -> list[dict[str, object]]:
    """Get CLI command examples - DRY pattern for example data.

    Returns:
        list[dict[str, object]]: List of CLI command examples with metadata.

    """
    return [
        {
            "name": "Show CLI Help",
            "command": ["flext-oracle", "--help"],
            "description": "Display all available CLI commands",
        },
        {
            "name": "Connect using Environment Variables",
            "command": ["flext-oracle", "connect-env", "--debug"],
            "description": "Connect to Oracle using environment variables",
            "env_required": True,
        },
        {
            "name": "List Database Schemas",
            "command": ["flext-oracle", "schemas"],
            "description": "List all available schemas",
            "env_required": True,
        },
        {
            "name": "List Database Tables",
            "command": ["flext-oracle", "tables"],
            "description": "List all tables",
            "env_required": True,
        },
        {
            "name": "Execute Simple Query",
            "command": [
                "flext-oracle",
                "query",
                "--sql",
                "SELECT SYSDATE FROM DUAL",
            ],
            "description": "Execute a simple query",
            "env_required": True,
        },
        {
            "name": "Check Database Health",
            "command": ["flext-oracle", "health"],
            "description": "Check database connection health",
            "env_required": True,
        },
        {
            "name": "Show Plugin Management",
            "command": ["flext-oracle", "plugins"],
            "description": "List and manage Oracle plugins",
            "env_required": True,
        },
        {
            "name": "Optimize Query",
            "command": [
                "flext-oracle",
                "optimize",
                "--sql",
                "SELECT * FROM USER_TABLES WHERE ROWNUM <= 10",
            ],
            "description": "Analyze and optimize SQL query",
            "env_required": True,
        },
    ]


def _run_example_command(example: dict[str, object]) -> None:
    """Run a single CLI example command - DRY pattern."""
    if example.get("env_required") and not _check_oracle_env():
        return

    command = example["command"]
    if isinstance(command, list):
        command_list = [str(item) for item in command]
    else:
        command_list = [str(command)]

    exit_code, stdout, stderr = run_cli_command(command_list)

    if exit_code == 0:
        if stdout.strip():
            # Show first few lines of output
            lines = stdout.strip().split("\n")
            preview = lines[:MAX_OUTPUT_LINES]
            if len(lines) > MAX_OUTPUT_LINES:
                preview.append("   ...")
            for _line in preview:
                pass
    elif stderr.strip():
        error_lines = stderr.strip().split("\n")[:2]  # Show first 2 error lines
        for _line in error_lines:
            pass


def _check_oracle_env() -> bool:
    """Check if Oracle environment variables are set - DRY pattern.

    Returns:
        bool: True if all required environment variables are set.

    """
    required_vars = [
        "FLEXT_TARGET_ORACLE_HOST",
        "FLEXT_TARGET_ORACLE_USERNAME",
        "FLEXT_TARGET_ORACLE_PASSWORD",
    ]
    return all(os.getenv(var) for var in required_vars)


def run_cli_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run CLI command and return exit code, stdout, stderr (no shell).

    Returns:
        tuple[int, str, str]: Exit code, stdout, and stderr from command execution.

    """

    def _run() -> tuple[int, str, str]:
        try:
            result = (
                FlextUtilities.FlextUtilities.CommandExecution.run_external_command(
                    cmd,
                    capture_output=True,
                    check=False,
                    timeout=30.0,
                )
            )
            if result.is_success:
                process = result.unwrap()
                return process.returncode, process.stdout, process.stderr
            return 1, "", f"Command failed: {result.error}"
        except Exception as e:
            return 1, "", f"Command failed: {e}"

    return _run()


def demo_cli_commands() -> None:
    """Execute CLI command demonstrations using DRY patterns."""
    examples = _get_cli_examples()

    if not _check_oracle_env():
        return

    # Run each example - refatoração DRY real
    for example in examples:
        if not example.get("interactive", False):
            _run_example_command(example)


def show_environment_setup() -> None:
    """Show how to set up environment for CLI usage."""
    setup_script = """
# Oracle Database Configuration
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="flext_user"
export FLEXT_TARGET_ORACLE_PASSWORD="secure_password"

# Optional: Connection Pool Settings
export FLEXT_TARGET_ORACLE_POOL_MIN="1"
export FLEXT_TARGET_ORACLE_POOL_MAX="10"
export FLEXT_TARGET_ORACLE_TIMEOUT="30"

# Optional: Debug Mode
export FLEXT_CLI_DEV_MODE="true"
export FLEXT_CLI_LOG_LEVEL="debug"
"""

    env_file = Path(".env")
    if not env_file.exists():
        with env_file.open("w", encoding="utf-8") as f:
            f.write(setup_script.strip())


def show_docker_example() -> None:
    """Show Docker example for testing."""


def main() -> None:
    """Execute main CLI demonstration."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            show_environment_setup()
        elif sys.argv[1] == "docker":
            show_docker_example()
        elif sys.argv[1] == "demo":
            demo_cli_commands()
    else:
        # Show current environment status
        env_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_USERNAME",
        ]

        configured = sum(1 for var in env_vars if os.getenv(var))

        if configured == 0 or configured == len(env_vars):
            pass


if __name__ == "__main__":
    main()
