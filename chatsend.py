# chatsend.py
"""
Sends prompts to configured LLM endpoints using litellm and processes responses.
Adds a check to ensure the local server is running if target='local'.
Uses standard print for output, no click dependency.
Relies on llama_man.py to handle its own paths correctly.
"""
import sys
import os
import litellm
import resp_fmt

# --- Assumed import ---
# Assuming llama_man is importable (e.g., via sys.path or structure)
try:
    # Assuming llama_man is in an accessible path relative to the client
    # Adjust the path if necessary, e.g., by adding the server directory to sys.path
    # or packaging it properly.
    # For example:
    sys.path.append('../helloworld-llama-server') # If client and server are siblings
    import llama_man
    llama_man_imported = True
except ImportError:
    print(f"Error: Could not import 'llama_man'. Ensure the helloworld-llama-server"
          f" directory is accessible in the Python path.", file=sys.stderr)
    llama_man = None # Still useful for graceful failure in _get_config
    llama_man_imported = False
# --- End Assumed import ---

# --- Configuration ---
# api_base now correctly uses llama_man.PORT if available
LLM_CONFIGS = {
    'local': {
        'model': 'openai/gemma-3-1b-it-Q4_K_M.gguf',
        'api_base': f'http://127.0.0.1:{llama_man.PORT}/v1' if llama_man_imported else 'http://127.0.0.1:8012/v1',
        'api_key': 'dummy-key',
    },
    'openrouter': {
        'model': 'openrouter/google/gemma-3-1b-it:free',
        'api_key': os.environ.get("OPENROUTER_API_KEY"),
    }
}
# --- End Configuration ---

def _get_config(target: str) -> dict | None:
    """Retrieves configuration for the specified target."""
    config = LLM_CONFIGS.get(target)
    if not config:
        print(f"Error: Unknown target '{target}'. Available targets: {list(LLM_CONFIGS.keys())}", file=sys.stderr)
        return None
    if target == 'openrouter' and not config.get('api_key'):
        if not os.environ.get("OPENROUTER_API_KEY"):
             print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
             return None
        config['api_key'] = os.environ.get("OPENROUTER_API_KEY")
    # Update api_base dynamically - no change needed here
    if llama_man_imported and target == 'local':
         config['api_base'] = f'http://127.0.0.1:{llama_man.PORT}/v1'

    return config

def send_and_process(prompt: str, target: str = 'local') -> list[str]:
    """
    Sends the prompt using litellm. Checks local server status if target='local'.
    Relies on llama_man.py for correct path handling.
    """
    # --- Check Local Server Status (if target is 'local') ---
    if target == 'local':
        if not llama_man_imported:
             print("Error: Cannot check local server status because 'llama_man' module failed to import.", file=sys.stderr)
             return []

        # Call llama_man function - it uses its internal path logic now
        print("Target is 'local', checking server status...")
        status_code, message = llama_man.ensure_server_running_or_fail()

        # Status handling remains the same...
        if status_code == "RUNNING":
            print(f"Server check: {message}")
        elif status_code == "FAILED_START":
            print(f"Error: Server check failed: {message}", file=sys.stderr)
            print("Aborting prompt.")
            return []
        else: # Unexpected status
            print(f"Warning: Unexpected server status from check: {status_code} - {message}", file=sys.stderr)
            print("Aborting prompt.")
            return []
        print("Server confirmed running or auto-started.")
    # --- End Server Check ---

    config = _get_config(target)
    if not config:
        return []

    messages = [{"role": "user", "content": prompt}]
    full_response = ""

    litellm_args = {
        'model': config['model'],
        'messages': messages,
        'api_key': config.get('api_key'),
        'stream': True,
    }

    if target != 'openrouter' and 'api_base' in config:
        litellm_args['api_base'] = config['api_base']

    print(f"Sending prompt to target '{target}' (Model: {config['model']}, Endpoint: {config.get('api_base', 'Default for target')})...")
    try:
        litellm.drop_params = True
        stream = litellm.completion(**litellm_args)

        print("--- Response Stream ---")
        for chunk in stream:
             if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                 content = chunk.choices[0].delta.content
                 print(content, end='', flush=True)
                 full_response += content
        print("\n--- End of Stream ---")

    # Exception handling remains the same...
    except litellm.exceptions.APIConnectionError as e:
        api_base_info = f"'{config.get('api_base', 'Default for ' + target)}'"
        print(f"\nError [LiteLLM]: Cannot connect to API Base {api_base_info}.", file=sys.stderr)
        print(f"   Check if the server/service is running and configuration is correct.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        return []
    # ... (other exceptions remain the same) ...
    except Exception as e:
        print(f"\nAn unexpected error occurred during LiteLLM chat streaming: {e}", file=sys.stderr)
        print(f"Error Type: {type(e).__name__}", file=sys.stderr)
        return []

    if not full_response:
        print("Warning: No response content received from chat endpoint.", file=sys.stderr)
        return []

    code_blocks = resp_fmt.extract_code_blocks(full_response)

    return code_blocks