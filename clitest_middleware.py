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
import resp_fmt

@click.command()
@click.option('--product', required=True, help='The target product (e.g., Splunk OpenTelemetry Collector, curl).')
@click.option('--operation', required=True, help='The operation (e.g., install, uninstall, configure, chat).')
# Set target and mode to case_sensitive=False
@click.option('--target', default='local', type=click.Choice(['local', 'openrouter'], case_sensitive=False),
              help='The target LLM endpoint. Default: local.')
@click.option('--mode', default='execute', type=click.Choice(['execute', 'fix', 'chat'], case_sensitive=False),
              help='Interaction mode: execute (default), fix errors, or chat.')
@click.option('--msg', default=None, type=str,
              help='Optional message (e.g., chat text, error details, OS info).')
def main_command(product: str, operation: str, target: str, mode: str, msg: Optional[str]):
    """
    Agentic Middleware CLI to get assistance for product operations via LLM.
    """
    # Call the workflow handler to get the raw response
    # Changed variable name from final_output_string to full_response
    full_response = llm_workflow.handle_request(
        product=product,
        operation=operation,
        target=target,
        mode=mode,
        msg=msg
    )

    # --- Handle Final Output ---
    if full_response is not None:
        # --- >>> PROCESS AND FORMAT RESPONSE HERE <<< ---
        # 1. Extract code blocks from the full response
        code_blocks = resp_fmt.extract_code_blocks(full_response)

        # 2. Format the extracted blocks for display
        display_output = resp_fmt.format_code_blocks_for_display(code_blocks)

        # 3. Print the formatted output
        click.echo(display_output)
        # --- >>> END OF RESPONSE PROCESSING <<< ---
    else:
        # Error occurred, message likely printed already in lower layers
        click.echo("\nWorkflow completed with errors.", err=True)
        sys.exit(1)

# Export the command function for main.py
cli = main_command