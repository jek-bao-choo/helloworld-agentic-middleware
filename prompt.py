# prompt.py
"""
Stores the predefined prompts for the client.
"""

# For this simple case, we only have one prompt.
# In a real scenario, you might have a dictionary or function
# to select prompts based on product/operation.
INSTALL_CURL_MACOS = "What is command to install curl in MacOS? Keep it short. Also when is your knowledge cutoff?"

# You could add more prompts here later, e.g.:
# INSTALL_SPLUNK_OTEL_LINUX = "Show me the steps to install splunk-otel-collector on Linux"

# Export the specific prompt we'll use for now
default_prompt = INSTALL_CURL_MACOS