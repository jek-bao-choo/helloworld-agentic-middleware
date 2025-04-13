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
from local_server_manager import LocalServerManager # Needed to get port for config

# Instantiate manager once
_server_manager = LocalServerManager()

# --- Helper Function ---
def _clean_key_part(part: str) -> str:
    """Cleans string for use in dictionary keys (uppercase, replace non-alphanum with _)."""
    part = part.strip().upper()
    part = re.sub(r'\W+', '_', part) # Replace one or more non-alphanumeric with _
    part = re.sub(r'_+', '_', part)   # Collapse multiple underscores
    part = part.strip('_')          # Remove leading/trailing underscores
    return part

# --- Prompt Mapping Definition ---
# Define cleaned keys for operations and products
INSTALL = _clean_key_part("install")
UNINSTALL = _clean_key_part("uninstall")
UPGRADE = _clean_key_part("upgrade") # Example: Add if needed
CONFIGURE = _clean_key_part("configure") # Example: Add if needed

CURL = _clean_key_part("curl")
SPLUNK_OTEL = _clean_key_part("splunk-otel-collector")
# Add other products as needed:
# SPLUNK_OTEL_CHART = _clean_key_part("splunk-otel-collector-chart")
# DATADOG_AGENT = _clean_key_part("datadog-agent")
# GRAFANA_AGENT = _clean_key_part("grafana-agent")

# Map (OPERATION, PRODUCT) tuples to specific prompt variables for 'execute' mode
# Only add entries here if a specific prompt exists in llm_prompt.py
EXECUTE_PROMPT_MAP = {
    (INSTALL, CURL): llm_prompt.INSTALL_CURL,
    (INSTALL, SPLUNK_OTEL): llm_prompt.INSTALL_SPLUNK_OTEL_COLLECTOR,
    (UNINSTALL, SPLUNK_OTEL): llm_prompt.UNINSTALL_SPLUNK_OTEL_COLLECTOR,
    # Add other specific combinations here, mapping to variables in llm_prompt.py
    # e.g., (CONFIGURE, SPLUNK_OTEL): llm_prompt.CONFIGURE_SPLUNK_OTEL_COLLECTOR,
}

def _get_prompt(product: str, operation: str, mode: str, msg: Optional[str]) -> Optional[str]: # mode is now str
    """
    Gets the final prompt string based on mode, product, and operation using dictionary mapping.
    1. Handles 'fix' and 'chat' modes directly using specific templates.
    2. For 'execute' mode, looks up (operation, product) in EXECUTE_PROMPT_MAP.
    3. Falls back to CHAT template if no specific mapping found for 'execute'.
    4. Formats the chosen template with product, operation, mode, and msg.
    """
    prompt_template: Optional[str] = None
    prompt_name: str = "N/A" # For logging purposes
    msg_content = msg if msg else "N/A"
    product_display = product.strip()
    operation_display = operation.strip()

    # 1. Handle explicit modes 'fix' and 'chat'
    if mode == 'fix':
        prompt_template = llm_prompt.FIX
        prompt_name = "FIX template"
        print(f"Info: Using mode '{mode}'. Selected prompt: {prompt_name}")
    elif mode == 'chat':
        prompt_template = llm_prompt.CHAT
        prompt_name = "CHAT template"
        print(f"Info: Using mode '{mode}'. Selected prompt: {prompt_name}")
    # 2. Handle 'execute' mode
    else: # This block now only runs if mode is 'execute' (or unexpected, though Click prevents that)
        # Ensure mode is treated as execute if somehow it wasn't fix/chat
        # This check is arguably less critical now Click enforces choices, but harmless as a safeguard.
        if mode != 'execute':
             print(f"Warning: Unexpected mode '{mode}' encountered despite Click choices. Processing as 'execute'.", file=sys.stderr)
             # No need to reassign mode = 'execute', just proceed

        op_key = _clean_key_part(operation)
        prod_key = _clean_key_part(product)
        lookup_key = (op_key, prod_key)

        # Get from map, default to CHAT if not found using .get()
        prompt_template = EXECUTE_PROMPT_MAP.get(lookup_key, llm_prompt.CHAT)

        # Update prompt_name for logging based on whether the key was found
        if lookup_key in EXECUTE_PROMPT_MAP:
             prompt_name = f"Mapped execute prompt for {operation}/{product}"
        else:
             prompt_name = "CHAT template (fallback for execute)"
        # Log the mode being handled
        print(f"Info: Mode is '{mode}'. Selected prompt: {prompt_name}")


    # 3. Format the chosen template
    if prompt_template:
        try:
            # mode is now always 'execute', 'fix', or 'chat' string
            final_prompt = prompt_template.format(
                product=product_display,
                operation=operation_display,
                mode=mode, # Pass the mode string directly
                msg=msg_content,
            )
            return final_prompt
        except KeyError as e:
            print(f"Error: Prompt template formatting failed for '{prompt_name}'. Missing key: {e}. Template snippet: '{prompt_template[:100]}...'", file=sys.stderr)
            return None
        except Exception as e:
             print(f"Error: Unexpected error formatting prompt '{prompt_name}': {e}", file=sys.stderr)
             return None
    else:
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

    # 3. Send Chat Request and get full response
    # Changed variable name from code_blocks to full_response
    full_response = chatsend.send_and_process(selected_prompt, target, config)
    if full_response is None:
        # Error message already printed in chatsend
        print("Error: Failed to get response from chat.", file=sys.stderr)
        return None # Propagate error

    # 4. Return Full Response (UI formatting removed)
    return full_response # <<< Return the raw response string