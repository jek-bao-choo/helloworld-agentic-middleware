# clitest_client.py
"""
Defines the command-line interface using Click.
Invokes the workflow directly.
"""
import click
import sys

# Direct import of the main workflow function
import llm_workflow # Still the entry point

@click.command()
@click.option('--product', required=True, help='The target product.')
@click.option('--operation', required=True, help='The operation to perform.')
@click.option('--target', default='local', type=click.Choice(['local', 'openrouter'], case_sensitive=False),
              help='The target LLM endpoint. Default: local.')
def main_command(product: str, operation: str, target: str):
    """
    CLI Client to get assistance for product operations.
    """
    # Directly call the workflow handler
    final_output_string = llm_workflow.handle_request(product, operation, target)

    # --- Handle Final Output ---
    if final_output_string is not None:
        click.echo(final_output_string)
    else:
        click.echo("\nWorkflow completed with errors.", err=True)
        sys.exit(1)

# Export the command function for main.py
cli = main_command