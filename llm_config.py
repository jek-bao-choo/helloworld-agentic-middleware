# llm_config.py
"""
Manages configuration for different LLM targets.
Accepts local port info for configuration retrieval.
"""
import os
from typing import Optional, Dict, Any

# Define template structure - port filled in by get_llm_config
_LLM_CONFIGS_TEMPLATE: Dict[str, Dict[str, Any]] = {
    'local': {
        'model': 'openai/gemma-3-1b-it-Q4_K_M.gguf',
        'api_base': 'http://127.0.0.1:{port}/v1', # Port placeholder
        'api_key': 'dummy-key',
    },
    'openrouter': {
        'model': 'openrouter/google/gemini-2.5-pro-exp-03-25:free',
        'api_key': os.environ.get("OPENROUTER_API_KEY"),
    }
}

def get_llm_config(target: str, local_port: Optional[int] = 8012) -> Optional[Dict[str, Any]]:
    """
    Retrieves and validates configuration for the specified LLM target.

    Args:
        target: The target endpoint ('local' or 'openrouter').
        local_port: The port number to use for the local target's api_base.

    Returns:
        The configuration dictionary (as a copy) or None if invalid.
    """
    config_template = _LLM_CONFIGS_TEMPLATE.get(target)
    if not config_template:
        print(f"Error: Unknown target '{target}'. Available targets: {list(_LLM_CONFIGS_TEMPLATE.keys())}", file=sys.stderr)
        return None

    config = config_template.copy() # Work with a copy

    if target == 'openrouter':
        api_key = config.get('api_key') or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY environment variable not set for target 'openrouter'.", file=sys.stderr)
            return None
        config['api_key'] = api_key

    if target == 'local':
        port_to_use = local_port if local_port else 8012
        config['api_base'] = config['api_base'].format(port=port_to_use)

    return config