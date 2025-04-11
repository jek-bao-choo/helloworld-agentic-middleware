# ui.py
"""
Handles formatting results for display.
"""
from typing import List

def format_code_blocks_for_display(code_blocks: List[str]) -> str:
    """
    Formats the extracted code blocks into a single string for display.
    # ... (implementation unchanged from previous DI example) ...
    """
    if not code_blocks:
        return "\nNo executable code blocks found in the response."
    output_parts = [f"\nFound {len(code_blocks)} code block(s):"]
    for i, block in enumerate(code_blocks):
        output_parts.append(f"\n--- Code Block {i+1} ---")
        output_parts.append(block)
        output_parts.append("----------------------")
    return "\n".join(output_parts)