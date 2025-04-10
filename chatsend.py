# chatsend.py
"""
Sends prompts to configured LLM endpoints using litellm and processes responses.
"""
import sys
import os
import litellm
import resp_fmt

# --- Configuration ---
LLM_CONFIGS = {
    'local': {
        'model': 'openai/gemma-3-1b-it-Q4_K_M.gguf', # Keep openai/ prefix for litellm if needed
        'api_base': 'http://127.0.0.1:8012/v1', # Default local server endpoint
        'api_key': 'dummy-key',
    },
    'openrouter': {
        'model': 'openrouter/google/gemma-3-1b-it:free', # Example model, adjust as needed
        # 'api_base' is intentionally omitted here for OpenRouter target
        # Litellm uses the model prefix 'openrouter/' to determine the API base
        'api_key': os.environ.get("OPENROUTER_API_KEY"), # Load key from environment variable
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
        # Check environment variable directly here for clarity
        if not os.environ.get("OPENROUTER_API_KEY"):
             print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
             return None
        # Assign the key to the config dict for consistent access later if needed elsewhere
        config['api_key'] = os.environ.get("OPENROUTER_API_KEY")

    return config

def send_and_process(prompt: str, target: str = 'local') -> list[str]:
    """
    Sends the prompt using litellm to the specified target, gets the response,
    and extracts code blocks.

    Args:
        prompt: The prompt string to send.
        target: The target endpoint ('local' or 'openrouter'). Defaults to 'local'.

    Returns:
        A list of strings, each representing a formatted code block from the response.
        Returns an empty list if the chat fails or no code blocks are found.
    """
    config = _get_config(target)
    if not config:
        return [] # Configuration error

    messages = [{"role": "user", "content": prompt}]
    full_response = ""

    # Prepare arguments for litellm.completion
    litellm_args = {
        'model': config['model'],
        'messages': messages,
        'api_key': config.get('api_key'), # Use .get() for safety, though checked in _get_config
        'stream': True,
    }

    # Conditionally add api_base ONLY if it's NOT the openrouter target
    if target != 'openrouter' and 'api_base' in config:
        litellm_args['api_base'] = config['api_base']

    print(f"Sending prompt to target '{target}' (Model: {config['model']})...")
    try:
        litellm.drop_params = True # Keep dropping potentially incompatible params
        # Pass the prepared arguments using dictionary unpacking (**)
        stream = litellm.completion(**litellm_args)

        print("--- Response Stream ---")
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                 content = chunk.choices[0].delta.content
                 print(content, end='', flush=True) # Print chunk immediately
                 full_response += content
        print("\n--- End of Stream ---")

    except litellm.exceptions.APIConnectionError as e:
        api_base_info = f"'{config.get('api_base', 'Default for ' + target)}'"
        print(f"\nError [LiteLLM]: Cannot connect to API Base {api_base_info}.", file=sys.stderr)
        print(f"   Check if the server/service is running and configuration is correct.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        return []
    except litellm.exceptions.AuthenticationError as e:
        print(f"\nError [LiteLLM]: Authentication failed for '{target}'. Check API key.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        return []
    except litellm.exceptions.APIError as e:
         print(f"\nError [LiteLLM]: API Error from '{target}'. Status: {e.status_code}", file=sys.stderr)
         print(f"   Details: {e}", file=sys.stderr)
         # Check for the specific missing protocol error again, although it shouldn't happen now
         if "missing an 'http://' or 'https://' protocol" in str(e):
              print("\n   Hint: This specific error occurred again. Check litellm version or report issue.", file=sys.stderr)
         return []
    except Exception as e:
        print(f"\nAn unexpected error occurred during LiteLLM chat streaming: {e}", file=sys.stderr)
        return []

    if not full_response:
        print("No response received from chat endpoint.", file=sys.stderr)
        return []

    # Format the response using resp_fmt
    code_blocks = resp_fmt.extract_code_blocks(full_response)

    return code_blocks