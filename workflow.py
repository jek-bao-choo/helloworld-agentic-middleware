# workflow.py
"""
Orchestrates the client workflow: prompt selection, chat execution, result display.
"""
import prompt     # Import the prompts
import chatsend   # Import the chat sending logic
import ui         # Import the UI logic

def handle_request(product: str, operation: str, target: str):
    """
    Handles the user request based on product, operation, and target endpoint.

    Args:
        product: The product name (e.g., "splunk-otel-collector").
        operation: The operation name (e.g., "install").
        target: The target LLM endpoint ('local' or 'openrouter').
    """
    print(f"Received request for product='{product}', operation='{operation}', target='{target}'")

    # --- Simple Logic ---
    # Ignore product/operation for now, use default prompt.
    # Future: Implement logic to select prompt based on inputs.
    selected_prompt = prompt.default_prompt
    print(f"Using prompt: '{selected_prompt}'")

    # Call chatsend to send the prompt to the specified target
    # and get formatted code blocks
    code_blocks = chatsend.send_and_process(selected_prompt, target=target)

    # Call the UI function to display the results
    ui.display_code_blocks(code_blocks)