# llm_workflow.py
"""
Orchestrates the client workflow: prompt generation (convention over configuration),
config retrieval, chat execution, result display.
"""
import sys
import re # Needed for cleaning keys
from typing import Optional

# Direct imports of dependencies
import llm_prompt       # Import the prompt components/templates
import llm_config       # For getting configuration
import chatsend         # Handles the sending process
import ui               # Handles formatting for final display
from local_server_manager import LocalServerManager # Needed to get port for config

# Instantiate manager once
_server_manager = LocalServerManager()

# --- Prompt Generation (Simplified - Convention over Configuration) ---
def _clean_key_part(part: str) -> str:
    """Cleans string for use in prompt variable lookup (uppercase, replace non-alphanum with _)."""
    part = part.strip().upper()
    part = re.sub(r'\W+', '_', part) # Replace one or more non-alphanumeric with _
    part = re.sub(r'_+', '_', part)   # Collapse multiple underscores
    part = part.strip('_')          # Remove leading/trailing underscores
    return part

def _get_prompt(product: str, operation: str, mode: str, msg: Optional[str]) -> Optional[str]:
    """
    Gets the final prompt string based on mode, product, and operation.
    1. Handles 'fix' and 'chat' modes directly using specific templates.
    2. For 'execute' mode, tries OPERATION_PRODUCT specific prompt first.
    3. Falls back to CHAT template if no specific prompt found for 'execute'.
    4. Formats the chosen template with product, operation, mode, and msg.
    """
    prompt_template: Optional[str] = None
    prompt_name: str = "N/A" # For logging purposes

    # Use provided msg or a default string if None
    msg_content = msg if msg else "N/A" # Renamed variable for clarity inside function

    # Prepare display versions (original case)
    product_display = product.strip()
    operation_display = operation.strip()

    # 1. Handle 'fix' and 'chat' modes directly
    if mode == 'fix':
        prompt_template = llm_prompt.FIX
        prompt_name = "FIX template"
        print(f"Info: Using mode '{mode}'. Selected prompt: {prompt_name}")
    elif mode == 'chat':
        prompt_template = llm_prompt.CHAT
        prompt_name = "CHAT template"
        print(f"Info: Using mode '{mode}'. Selected prompt: {prompt_name}")

    # 2. Handle 'execute' mode (default)
    else:
        if mode != 'execute':
             print(f"Warning: Unknown mode '{mode}'. Defaulting to 'execute' logic.", file=sys.stderr)
             mode = 'execute' # Treat unknown modes as execute

        # Try to find specific prompt by OPERATION_PRODUCT convention
        op_key = _clean_key_part(operation)
        prod_key = _clean_key_part(product)
        specific_prompt_name = f"{op_key}_{prod_key}"
        specific_prompt = getattr(llm_prompt, specific_prompt_name, None)

        if specific_prompt:
            prompt_template = specific_prompt
            prompt_name = specific_prompt_name
            print(f"Info: Mode is '{mode}'. Using specific prompt '{prompt_name}'.")
        else:
            # Fallback to CHAT template for execute mode if no specific prompt
            prompt_template = llm_prompt.CHAT # <<< Fallback to CHAT
            prompt_name = "CHAT template (fallback for execute)" # <<< Updated log message
            print(f"Info: Mode is '{mode}'. Specific prompt '{specific_prompt_name}' not found. Using fallback: {prompt_name}.")

    # 4. Format the chosen template
    if prompt_template:
        try:
            # Use .format() with msg=msg_content
            final_prompt = prompt_template.format(
                product=product_display,
                operation=operation_display,
                mode=mode,
                msg=msg_content, # Changed key to 'msg'
            )
            return final_prompt
        except KeyError as e:
            # This might happen if a placeholder exists but wasn't provided in .format() args
            print(f"Error: Prompt template formatting failed for '{prompt_name}'. Missing key: {e}. Template snippet: '{prompt_template[:100]}...'", file=sys.stderr)
            return None
        except Exception as e:
             print(f"Error: Unexpected error formatting prompt '{prompt_name}': {e}", file=sys.stderr)
             return None
    else:
        # This case should ideally not be reached with the new logic, but is a safeguard
        print(f"Error: Could not determine prompt template for {product}/{operation}/{mode}", file=sys.stderr)
        return None


# --- Main Workflow Logic ---
def handle_request(
    product: str,
    operation: str,
    target: str,
    mode: str,
    msg: Optional[str] # Changed parameter name to msg
) -> Optional[str]:
    """
    Handles the user request: gets prompt, gets config, sends chat, formats result.
    """
    # Use 'msg is not None' for logging clarity
    print(f"Info: Received request for product='{product}', operation='{operation}', target='{target}', mode='{mode}', msg='{msg is not None}'")

    # 1. Get Prompt (using revised logic above, passing msg)
    selected_prompt = _get_prompt(product, operation, mode, msg) # Pass msg
    if selected_prompt is None:
        return None

    # Prompt printing is now done in chatsend.py

    # 2. Get Configuration
    local_port = _server_manager.get_port()
    config = llm_config.get_llm_config(target, local_port)
    if not config:
        return None

    # 3. Send Chat Request
    # Pass the selected_prompt (which now incorporates msg content)
    code_blocks = chatsend.send_and_process(selected_prompt, target, config)
    if code_blocks is None:
        print("Error: Failed to get response from chat.", file=sys.stderr)
        return None # Indicate failure

    # 4. Format Results for UI
    display_output = ui.format_code_blocks_for_display(code_blocks)

    return display_output