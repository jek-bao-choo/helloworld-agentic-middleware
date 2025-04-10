# clitest_client.py
"""
Defines the command-line interface using Click.
(Previously cli_client.py)
"""
import click
import workflow # Import the workflow logic

@click.command()
@click.option('--product', required=True, help='The target product (e.g., splunk-otel-collector).')
@click.option('--operation', required=True, help='The operation to perform (e.g., install).')
@click.option('--target', default='local', type=click.Choice(['local', 'openrouter'], case_sensitive=False),
              help='The target LLM endpoint (local or openrouter). Default: local.')
def main_command(product: str, operation: str, target: str):
    """
    CLI Client to get assistance for product operations.

    Sends requests to either a local LLM server or OpenRouter.ai.
    Requires OPENROUTER_API_KEY environment variable if using target 'openrouter'.
    """
    # Pass arguments (including target) to the workflow handler
    workflow.handle_request(product, operation, target)

# Export the command function for main.py
cli = main_command