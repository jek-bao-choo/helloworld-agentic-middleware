# llm_workflow.py
"""
Orchestrates the client workflow: prompt generation (convention over configuration),
config retrieval, chat execution, result display.
"""
import sys
import re # Needed for cleaning keys
from typing import List, Optional, Dict

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

def _get_prompt(product: str, operation: str, mode: str, message: Optional[str]) -> Optional[str]:
    """
    Gets the final prompt string:
    1. Tries to find specific prompt by convention ([OP]_[PRODUCT]) in llm_prompt.
    2. Falls back to mode-based templates (EXECUTE, FIX, CHAT).
    3. Appends optional message for 'execute' and 'chat' modes.
    """
    prompt: Optional[str] = None
    base_template: Optional[str] = None
    product_display = product.strip() # Keep original case for formatting
    operation_display = operation.strip()

    # 1. Try to find specific prompt by naming convention
    op_key = _clean_key_part(operation)
    prod_key = _clean_key_part(product)
    specific_prompt_name = f"{op_key}_{prod_key}"

    specific_prompt = getattr(llm_prompt, specific_prompt_name, None) # Safely check if attr exists

    if specific_prompt:
        prompt = specific_prompt
        print(f"Info: Using specific prompt '{specific_prompt_name}'.")
        # Specific prompts are assumed to be complete and don't need base formatting
    else:
        # 2. Fallback to mode-based templates
        print(f"Info: No specific prompt '{specific_prompt_name}' found, using mode '{mode}'.")
        if mode == 'execute':
            base_template = llm_prompt.EXECUTE
        elif mode == 'fix':
            base_template = llm_prompt.FIX
            # For FIX mode, we insert the message/context *into* the template
            context = message if message else "No specific error details provided."
            try:
                prompt = base_template.format(product=product_display, operation=operation_display, context=context)
            except KeyError as e:
                 print(f"Error: FIX Prompt template formatting failed. Key: {e}. Template: {base_template}", file=sys.stderr)
                 return None
            # Prevent appending message again later for FIX mode
            message = None
        else: # Default/fallback to CHAT mode
            if mode != 'chat':
                print(f"Warning: Unknown mode '{mode}'. Using CHAT prompt template as fallback.", file=sys.stderr)
            base_template = llm_prompt.CHAT

        # Format the base template if not already done (i.e., for EXECUTE/CHAT)
        if base_template and not prompt:
            try:
                prompt = base_template.format(product=product_display, operation=operation_display)
            except KeyError as e:
                print(f"Error: Prompt template formatting failed. Key: {e}. Template: {base_template}", file=sys.stderr)
                return None

    # 3. Append optional message for relevant modes (if not already used in FIX)
    if prompt and message and mode in ['execute', 'chat']:
        prompt += f"\n\n--- Additional Context/Message ---\n{message}"
        print("Info: Appended provided message to prompt.")

    if not prompt:
         print(f"Error: Could not determine prompt for {product}/{operation}/{mode}", file=sys.stderr)
         return None

    return prompt


# --- Main Workflow Logic ---
def handle_request(
    product: str,
    operation: str,
    target: str,
    mode: str,
    message: Optional[str] # Accept optional message
) -> Optional[str]:
    """
    Handles the user request: gets prompt, gets config, sends chat, formats result.
    """
    print(f"Info: Received request for product='{product}', operation='{operation}', target='{target}', mode='{mode}', message='{message is not None}'")

    # 1. Get Prompt (using simplified logic)
    selected_prompt = _get_prompt(product, operation, mode, message)
    if selected_prompt is None:
        return None

    # Optional: Print final prompt for debugging
    # print(f"\n--- Final Generated Prompt ---\n{selected_prompt}\n----------------------------\n")

    # 2. Get Configuration
    local_port = _server_manager.get_port()
    config = llm_config.get_llm_config(target, local_port)
    if not config:
        return None

    # 3. Send Chat Request
    code_blocks = chatsend.send_and_process(selected_prompt, target, config)
    if code_blocks is None:
        print("Error: Failed to get response from chat.", file=sys.stderr)
        return None

    # 4. Format Results for UI
    display_output = ui.format_code_blocks_for_display(code_blocks)

    return display_output