# main.py
"""
Main entry point for the CLI application.
"""
# Import the exported command function from clitest_client.py (changed from cli_client)
from clitest_client import cli

if __name__ == '__main__':
    # Execute the Click command function
    cli()