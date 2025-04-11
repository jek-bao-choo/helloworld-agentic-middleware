# llm_interface.py
"""
Handles interaction with the LiteLLM library. Yields response chunks or raises errors.
"""
import sys
import litellm
from typing import Dict, Any, Iterator

# Custom Exceptions (keep these)
class LLMConnectionError(Exception): pass
class LLMAuthenticationError(Exception): pass
class LLMAPITError(Exception): pass
class LLMUnexpectedError(Exception): pass

def prepare_litellm_args(prompt: str, config: Dict[str, Any], target: str) -> Dict[str, Any]:
    # ... (implementation unchanged from previous DI example) ...
    messages = [{"role": "user", "content": prompt}]
    litellm_args = {
        'model': config['model'],
        'messages': messages,
        'api_key': config.get('api_key'),
        'stream': True,
    }
    if target != 'openrouter' and 'api_base' in config:
        litellm_args['api_base'] = config['api_base']
    return litellm_args

def stream_litellm_response(litellm_args: Dict[str, Any], config: Dict[str, Any], target: str) -> Iterator[str]:
    """
    Calls litellm.completion and yields response content chunks.
    Raises custom exceptions on failure.
    # ... (implementation unchanged from previous DI example) ...
    """
    endpoint_info = litellm_args.get('api_base', 'Default LiteLLM endpoint')
    print(f"Info: Sending prompt to target '{target}' (Model: {config['model']}, Endpoint: {endpoint_info})...")
    try:
        litellm.drop_params = True
        stream = litellm.completion(**litellm_args)
        found_content = False
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield content
                found_content = True
        if not found_content:
             print("Warning: No response content received from stream.", file=sys.stderr)
    except litellm.exceptions.APIConnectionError as e:
        raise LLMConnectionError(f"Cannot connect to API Base {endpoint_info}. Details: {e}") from e
    except litellm.exceptions.AuthenticationError as e:
        raise LLMAuthenticationError(f"Authentication failed for '{target}'. Check API key. Details: {e}") from e
    except litellm.exceptions.APIError as e:
         raise LLMAPITError(f"API Error from '{target}'. Status: {e.status_code}. Details: {e}") from e
    except Exception as e:
        raise LLMUnexpectedError(f"Unexpected error during LiteLLM call: {type(e).__name__}: {e}") from e