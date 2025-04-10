# ui.py
"""
Handles user interface elements like displaying results.
"""

def display_code_blocks(code_blocks: list[str]):
    """
    Displays the extracted code blocks to the user, one by one.

    Args:
        code_blocks: A list of strings, each a code block.
    """
    if not code_blocks:
        print("\nNo executable code blocks found in the response.")
        return

    print(f"\nFound {len(code_blocks)} code block(s):")
    for i, block in enumerate(code_blocks):
        print(f"\n--- Code Block {i+1} ---")
        print(block)
        print("----------------------")
        # Optional: Add interaction for running commands later
        # if i < len(code_blocks) - 1:
        #     input("Press Enter to view the next code block...")