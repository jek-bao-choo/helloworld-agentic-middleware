# clitest_middleware.py (Previously clitest_client.py)
"""
Defines the command-line interface using Click.
Invokes the workflow directly.
"""
import click
import sys
from typing import Optional

# Direct import of the main workflow function
import llm_workflow

@click.command()
@click.option('--product', required=True, help='The target product (e.g., Splunk OpenTelemetry Collector, curl).')
@click.option('--operation', required=True, help='The operation (e.g., install, uninstall, configure, chat).')
# Set target and mode to case_sensitive=False
@click.option('--target', default='local', type=click.Choice(['local', 'openrouter'], case_sensitive=False),
              help='The target LLM endpoint. Default: local.')
@click.option('--mode', default='execute', type=click.Choice(['execute', 'fix', 'chat'], case_sensitive=False),
              help='Interaction mode: execute steps, fix errors, or chat.')
@click.option('--msg', default=None, type=str,
              help='Optional message (e.g., chat text, error details, OS info).')
def main_command(product: str, operation: str, target: str, mode: str, msg: Optional[str]):
    """
    Agentic Middleware CLI to get assistance for product operations via LLM.
    """
    # Call the workflow handler, passing the 'msg' variable correctly
    final_output_string = llm_workflow.handle_request(
        product=product,
        operation=operation,
        target=target,
        mode=mode,
        msg=msg
    )

    # --- Handle Final Output ---
    if final_output_string is not None:
        click.echo(final_output_string)
    else:
        click.echo("\nWorkflow completed with errors.", err=True)
        sys.exit(1)

# Export the command function for main.py
cli = main_command