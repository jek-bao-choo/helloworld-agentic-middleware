# llm_workflow.py
"""
Orchestrates the client workflow: prompt selection, config retrieval,
chat execution, result display.
"""
import sys
from typing import Optional

# Direct imports of dependencies
import llm_prompt         # For getting prompts
import llm_config         # For getting configuration
import chatsend           # Handles the sending process
import ui                 # Handles formatting for final display
from local_server_manager import LocalServerManager # Needed to get port for config

# Instantiate manager once for workflow use (getting port)
# Could also be passed in if needed elsewhere
_server_manager = LocalServerManager()

def _get_prompt(product: str, operation: str) -> Optional[str]:
    """Selects the appropriate prompt."""
    # Simple logic for now
    try:
        print(f"Info: Selecting default prompt (ignoring product/operation).")
        return llm_prompt.default_prompt
    except AttributeError:
        print("Error: default_prompt not found in llm_prompt module.", file=sys.stderr)
        return None

def handle_request(product: str, operation: str, target: str) -> Optional[str]:
    """
    Handles the user request based on product, operation, and target endpoint.

    Args:
        product: The product name.
        operation: The operation name.
        target: The target LLM endpoint.

    Returns:
        A string formatted for display, or None if an error occurs.
    """
    print(f"Info: Received request for product='{product}', operation='{operation}', target='{target}'")

    # 1. Get Prompt
    selected_prompt = _get_prompt(product, operation)
    if selected_prompt is None:
        return None # Error message printed by _get_prompt

    # 2. Get Configuration
    local_port = _server_manager.get_port() # Get port needed for config
    config = llm_config.get_llm_config(target, local_port)
    if not config:
        return None # Error message printed by get_llm_config

    # 3. Send Chat Request (passes config to chatsend)
    code_blocks = chatsend.send_and_process(selected_prompt, target, config) # Pass config here

    if code_blocks is None:
        print("Error: Failed to get response from chat.", file=sys.stderr)
        return None

    # 4. Format Results for UI
    display_output = ui.format_code_blocks_for_display(code_blocks)

    return display_output