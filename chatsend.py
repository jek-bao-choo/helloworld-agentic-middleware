# chatsend.py
"""
Sends prompts to configured LLM endpoints using litellm and processes responses.
"""
import sys
import os
import litellm
import resp_fmt


# --- Assumed import ---
# This assumes llama_man.py (and its dependency llama_pid.py)
# are accessible in the Python path when running the client.
try:
    # Assuming llama_man is in an accessible path relative to the client
    # Adjust the path if necessary, e.g., by adding the server directory to sys.path
    # or packaging it properly.
    # For example:
    import sys
    sys.path.append('../helloworld-llama-server') # If client and server are siblings
    import llama_man
except ImportError:
    # Use print to stderr for errors
    print("Error: Could not import 'llama_man'. Ensure the helloworld-llama-server"
          " directory is accessible in the Python path.", file=sys.stderr)
    llama_man = None # Set to None to handle downstream errors gracefully
# --- End Assumed import ---

# --- Configuration ---
LLM_CONFIGS = {
    'local': {
        'model': 'openai/gemma-3-1b-it-Q4_K_M.gguf',
        # Use the PORT exported from llama_man if available and imported
        'api_base': f'http://127.0.0.1:{llama_man.PORT}/v1' if llama_man else 'http://127.0.0.1:8012/v1',
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
        # Use print to stderr for errors
        print(f"Error: Unknown target '{target}'. Available targets: {list(LLM_CONFIGS.keys())}", file=sys.stderr)
        return None
    if target == 'openrouter' and not config.get('api_key'):
        if not os.environ.get("OPENROUTER_API_KEY"):
             # Use print to stderr for errors
             print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
             return None
        config['api_key'] = os.environ.get("OPENROUTER_API_KEY")
    # Update api_base dynamically if llama_man was imported successfully
    if llama_man and target == 'local':
         config['api_base'] = f'http://127.0.0.1:{llama_man.PORT}/v1'

    return config

def send_and_process(prompt: str, target: str = 'local') -> list[str]:
    """
    Sends the prompt using litellm to the specified target, gets the response,
    and extracts code blocks. Checks if local server is running first if target='local'.
    Uses standard print for output.

    Args:
        prompt: The prompt string to send.
        target: The target endpoint ('local' or 'openrouter'). Defaults to 'local'.

    Returns:
        A list of strings, each representing a formatted code block from the response.
        Returns an empty list if the chat fails or no code blocks are found.
    """
    # --- Check Local Server Status (if target is 'local') ---
    if target == 'local':
        if not llama_man: # Check if import failed earlier
             print("Error: Cannot check local server status because 'llama_man' module failed to import.", file=sys.stderr)
             return [] # Abort sending

        print("Target is 'local', checking server status...")
        status_code, message = llama_man.ensure_server_running_or_fail()

        if status_code == "RUNNING":
            # Use standard print for feedback
            print(f"Server check: {message}") # Positive feedback to stdout
        elif status_code == "FAILED_START":
            # Use print to stderr for errors
            print(f"Error: Server check failed: {message}", file=sys.stderr)
            print("Aborting prompt.")
            return [] # Return empty list to indicate failure
        else: # Unexpected status
            # Use print to stderr for warnings/unexpected
            print(f"Warning: Unexpected server status from check: {status_code} - {message}", file=sys.stderr)
            print("Aborting prompt.")
            return [] # Return empty list
        print("Server confirmed running or auto-started.")
    # --- End Server Check ---

    config = _get_config(target)
    if not config:
        # Error message already printed by _get_config to stderr
        return [] # Configuration error

    messages = [{"role": "user", "content": prompt}]
    full_response = ""

    # Prepare arguments for litellm.completion
    litellm_args = {
        'model': config['model'],
        'messages': messages,
        'api_key': config.get('api_key'),
        'stream': True,
    }

    # Conditionally add api_base
    if target != 'openrouter' and 'api_base' in config:
        litellm_args['api_base'] = config['api_base']

    # Use standard print for info message
    print(f"Sending prompt to target '{target}' (Model: {config['model']}, Endpoint: {config.get('api_base', 'Default for target')})...")
    try:
        litellm.drop_params = True
        stream = litellm.completion(**litellm_args)

        # Use standard print for stream header
        print("--- Response Stream ---")
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                 content = chunk.choices[0].delta.content
                 # Use standard print for streaming output
                 print(content, end='', flush=True)
                 full_response += content
        # Use standard print for stream footer (with newline)
        print("\n--- End of Stream ---")

    except litellm.exceptions.APIConnectionError as e:
        api_base_info = f"'{config.get('api_base', 'Default for ' + target)}'"
        # Use print to stderr for errors
        print(f"\nError [LiteLLM]: Cannot connect to API Base {api_base_info}.", file=sys.stderr)
        print(f"   Check if the server/service is running and configuration is correct.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        return []
    except litellm.exceptions.AuthenticationError as e:
        # Use print to stderr for errors
        print(f"\nError [LiteLLM]: Authentication failed for '{target}'. Check API key.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        return []
    except litellm.exceptions.APIError as e:
         # Use print to stderr for errors
         print(f"\nError [LiteLLM]: API Error from '{target}'. Status: {e.status_code}", file=sys.stderr)
         print(f"   Details: {e}", file=sys.stderr)
         return []
    except Exception as e:
        # Use print to stderr for errors
        print(f"\nAn unexpected error occurred during LiteLLM chat streaming: {e}", file=sys.stderr)
        print(f"Error Type: {type(e).__name__}", file=sys.stderr)
        return []

    if not full_response:
        # Use print to stderr for warnings
        print("Warning: No response content received from chat endpoint.", file=sys.stderr)
        return []

    # Format the response using resp_fmt
    code_blocks = resp_fmt.extract_code_blocks(full_response)

    return code_blocks