# main.py
"""
Main entry point for the CLI application.
"""
# Import the exported command function from clitest_middleware.py (changed from cli_client)
from clitest_middleware import cli

if __name__ == '__main__':
    # Execute the Click command function
    cli()