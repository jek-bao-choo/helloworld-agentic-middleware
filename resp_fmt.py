# resp_fmt.py
"""
Formats the response from the chat model, extracting code blocks
(both triple-backtick fenced blocks and single-backtick inline code).
"""
import re
import sys # Added for debug print if needed

def extract_code_blocks(response_text: str) -> list[str]:
    """
    Extracts code blocks, including both triple-backtick fenced blocks
    and single-backtick inline code spans.

    Args:
        response_text: The raw text response from the chat model.

    Returns:
        A list of strings, where each string is a matched code block/span
        (including the backticks). Returns an empty list if none found.
    """
    # Pattern for triple-backtick blocks (captures block in group 1)
    # Made final \n optional and added optional whitespace before closing ```
    triple_tick_pattern = r"(```(\w+)?\s*\n(.*?)\n?\s*```)"

    # Pattern for single-backtick inline code (captures span in group 4)
    # Looks for non-backtick, non-newline characters between single backticks
    # to target single-line commands primarily.
    single_tick_pattern = r"(`([^`\n]+?)`)" # Group 4 is the whole match, Group 5 is content

    # Combined pattern using alternation (|)
    # It will try to match the triple_tick_pattern first, then the single_tick_pattern.
    combined_pattern = f"{triple_tick_pattern}|{single_tick_pattern}"

    formatted_blocks = []
    # Use finditer with the combined pattern and DOTALL for the triple-tick part
    for match_obj in re.finditer(combined_pattern, response_text, re.DOTALL):
        # Add the entire matched string (group 0), whether it was triple or single ticks
        formatted_blocks.append(match_obj.group(0))

    # Debugging print (optional: remove after confirming fix)
    # if not formatted_blocks and ("```" in response_text or "`" in response_text):
    #    print(f"Debug: No blocks found by combined regex. Raw text contained backticks:\n---\n{response_text}\n---", file=sys.stderr)
    # elif formatted_blocks:
    #    print(f"Debug: Found blocks/spans: {formatted_blocks}", file=sys.stderr)


    return formatted_blocks