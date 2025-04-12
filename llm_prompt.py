# llm_prompt.py
"""
Stores reusable components, basic templates, and specific prompts.
Uses triple quotes for easier multiline/XML definition.
"""

# --- Basic Templates by Mode (Simplified Names) ---
# Using triple quotes for easier multiline definitions and XML inclusion
EXECUTE = """Provide step-by-step instructions with commands to {operation} {product}.
Ensure commands are in executable code blocks.
<context>Be concise and clear.</context>"""

FIX = """A user encountered an error while trying to {operation} {product}.
What are common troubleshooting steps and how can they diagnose the issue?
<user_context>
{context}
</user_context>
Ask clarifying questions if needed."""

CHAT = """Tell me about {operation} {product}.
<instructions>Explain its purpose and key aspects based on general knowledge.</instructions>"""

# --- Specific Prompts (Use Uppercase Convention: OPERATION_PRODUCT) ---
# These override the general mode templates when matched by llm_workflow.py
# Using triple quotes allows formatting and potential XML easily.
INSTALL_CURL = """Provide the single command to install curl on macOS using Homebrew.
<output_format>Only the command in a bash code block.</output_format>"""

INSTALL_SPLUNK_OTEL_COLLECTOR = """Generate a concise shell script to download and install the Splunk OpenTelemetry Collector on a standard Linux system using the default settings.
<output_format>Ensure the script is in a single executable bash code block.</output_format>"""

UNINSTALL_SPLUNK_OTEL_COLLECTOR = """Provide the commands to completely uninstall the Splunk OpenTelemetry Collector from a standard Linux system, including removing configuration and data directories.
<output_format>Place commands in bash code blocks.</output_format>"""

# Add more specific prompts here, following the OPERATION_PRODUCT naming convention
# e.g., CONFIGURE_SPLUNK_OTEL_COLLECTOR = """..."""