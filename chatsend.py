# chatsend.py
"""
Handles sending a chat request and processing the response stream.
Requires configuration to be passed in.
"""
import sys
from typing import List, Optional, Dict, Any

# Direct imports of dependencies
import llm_interface # Handles actual litellm calls
from local_server_manager import LocalServerManager # Manages local server

# Lazily instantiated manager (kept internal to this module)
_server_manager_instance: Optional[LocalServerManager] = None

def _get_server_manager() -> LocalServerManager:
    """Gets or creates the singleton server manager instance."""
    global _server_manager_instance
    if _server_manager_instance is None:
        _server_manager_instance = LocalServerManager()
    return _server_manager_instance


# --- Only Public Method ---
def send_and_process(
    prompt: str,
    target: str,
    config: Dict[str, Any] # Configuration MUST be provided now
) -> str | None | Any:
    """
    Sends prompt, checks server, calls LLM interface, processes response.

    Args:
        prompt: The prompt string to send.
        target: The target endpoint ('local' or 'openrouter').
        config: The LLM configuration dictionary for the target.

    Returns:
        A list of strings (code blocks) if successful, None on error.
    """
    server_manager = _get_server_manager() # Get manager instance

    # 1. Check local server if applicable (internal detail of sending to local)
    if target == 'local':
        if not server_manager.ensure_running():
            print("Aborting prompt due to local server issue.")
            return None

    # --- >>> ADD THIS BLOCK TO PRINT THE PROMPT <<< ---
    # Use standard print, no need for click here
    print("\n--- Start of Final Prompt for LLM ---")
    print(prompt)
    print("--- End of Final Prompt for LLM ---\n")
    # --- >>> END OF ADDED BLOCK <<< ---

    # 2. Prepare Arguments (using provided config)
    # Config lookup is no longer done here
    llm_args = llm_interface.prepare_litellm_args(prompt, config, target)

    # 3. Execute Chat and Stream Response (calls llm_interface)
    full_response = ""
    try:
        response_stream = llm_interface.stream_litellm_response(llm_args, config, target)
        print("--- Start of Response Stream ---") # Keep progress print
        for chunk in response_stream:
             print(chunk, end='', flush=True)
             full_response += chunk
        print("\n--- End of Response Stream ---")

    except (llm_interface.LLMConnectionError,
            llm_interface.LLMAuthenticationError,
            llm_interface.LLMAPITError,
            llm_interface.LLMUnexpectedError) as e:
        print(f"\nError during chat execution: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"\nUnexpected error processing stream in chatsend: {type(e).__name__}: {e}", file=sys.stderr)
        return None

    # 4. Return Full Response (Code block extraction removed)
    # If the stream was empty but there was no error, return the empty string
    if not full_response and "Error" not in full_response: # Basic check if error wasn't caught
        print("Warning: No final response content accumulated.", file=sys.stderr)
        # Depending on desired behavior, could return "" or None here.
        # Returning "" seems more appropriate if the LLM just gave no output.
        return ""

    # Return the accumulated full_response string
    return full_response # <<< Return the raw string