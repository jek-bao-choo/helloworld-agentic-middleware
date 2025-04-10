# resp_fmt.py
"""
Formats the response from the chat model, extracting code blocks.
"""
import re

def extract_code_blocks(response_text: str) -> list[str]:
    """
    Extracts code blocks enclosed in triple backticks with language specifier.

    Args:
        response_text: The raw text response from the chat model.

    Returns:
        A list of strings, where each string is a code block
        (including the backticks and language identifier).
        Returns an empty list if no blocks are found.
    """
    # Regex to find ```language\ncode\n``` blocks
    pattern = r"```(\w+)?\s*\n(.*?)\n```"
    formatted_blocks = []
    # Use finditer to preserve the exact original block string including ``` markers
    for match_obj in re.finditer(pattern, response_text, re.DOTALL):
        formatted_blocks.append(match_obj.group(0))

    return formatted_blocks