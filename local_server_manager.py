# local_server_manager.py
"""
Abstracts the interaction with the llama_man module for managing the local server.
"""
import sys
import os
from typing import Optional

_SERVER_MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helloworld-llama-server'))

class LocalServerManager:
    """Manages the lifecycle and status checks for the local LLM server."""
    def __init__(self):
        self._llama_man = self._import_llama_man()

    def _import_llama_man(self):
        # ... (implementation unchanged from previous DI example) ...
        if _SERVER_MODULE_PATH not in sys.path:
             sys.path.append(_SERVER_MODULE_PATH)
        try:
            import llama_man
            print(f"Info: Successfully imported llama_man from {_SERVER_MODULE_PATH}")
            return llama_man
        except ImportError:
            print(f"Error: Could not import 'llama_man' from expected path: {_SERVER_MODULE_PATH}", file=sys.stderr)
            print(f"  Ensure '{_SERVER_MODULE_PATH}' exists and is correct relative to the client.", file=sys.stderr)
            return None


    def ensure_running(self) -> bool:
        # ... (implementation unchanged from previous DI example) ...
        if not self._llama_man:
            print("Error: Cannot check local server status because 'llama_man' module is not available.", file=sys.stderr)
            return False
        print("Target is 'local', checking server status...")
        status_code, message = self._llama_man.ensure_server_running_or_fail()
        if status_code == "RUNNING":
            print(f"Server check: {message}")
            print("Server confirmed running or auto-started.")
            return True
        elif status_code == "FAILED_START":
            print(f"Error: Server check failed: {message}", file=sys.stderr)
            return False
        else: # Unexpected status
            print(f"Warning: Unexpected server status from check: {status_code} - {message}", file=sys.stderr)
            return False

    def get_port(self) -> Optional[int]:
        # ... (implementation unchanged from previous DI example) ...
        if self._llama_man:
            return getattr(self._llama_man, 'PORT', None)
        return None