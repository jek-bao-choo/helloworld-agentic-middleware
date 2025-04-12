# llm_prompt.py
"""
Stores reusable components, basic templates, and specific prompts.
Uses triple quotes for easier multiline/XML definition.
"""

# --- Basic Templates by Mode (Simplified Names) ---
# Using triple quotes for easier multiline definitions and XML inclusion
FIX = """
Your task is to propose a fix for an issue encountered while trying to {operation} {product}. Here is the input context:
<input_context>
Operating System: MacOS
</inpt_context>

You must place commands in bash code blocks.
"""

CHAT = """
Your task is to answer questions about {operation} {product} topic. DO NOT answer any question beyond this topic.

<input_context>
{msg}
</inpt_context>

You must place commands in bash code blocks if it exists.
"""

# --- Specific Prompts (Use Uppercase Convention: OPERATION_PRODUCT) ---
# These override the general mode templates when matched by llm_workflow.py
# Using triple quotes allows formatting and potential XML easily.
INSTALL_CURL = """
You need to provide a command to check if curl is installed. If it is not installed, you need provide the command to install curl. Here is the input context:
<input_context>
Operating System: MacOS
</inpt_context>

You must place commands in bash code blocks.
"""

INSTALL_SPLUNK_OTEL_COLLECTOR = """
You need to provide a command to check if Splunk OpenTelemetry Collector is installed. If it is not installed, you need provide the command to install splunk-otel-collector. Here are the input context and examples:
<input_context>
Operating System: MacOS
SPLUNK_REALM: AU0
SPLUNK_TOKEN: dummy-token
</inpt_context>

<linux-examples>
1. Ensure you have systemd, curl and sudo installed.

2. Download and run the installer script using this command:
```bash
curl -sSL https://dl.signalfx.com/splunk-otel-collector.sh > /tmp/splunk-otel-collector.sh;
sudo sh /tmp/splunk-otel-collector.sh --realm $SPLUNK_REALM --memory $SPLUNK_MEMORY_TOTAL_MIB -- $SPLUNK_ACCESS_TOKEN
```

3. Replacing the following variables for your environment:

* SPLUNK_REALM: This is the Realm to send data to. The default is us0. To find your Splunk realm, see Note about realms.

* SPLUNK_MEMORY_TOTAL_MIB: This is the total allocated memory in mebibytes (MiB). For example, 512 allocates 512 MiB (500 x 2^20 bytes) of memory.

* SPLUNK_ACCESS_TOKEN: This is the base64-encoded access token for authenticating data ingest requests. See Create and manage organization access tokens using Splunk Observability Cloud.
</linux-examples>

<windows-examples>
The installer script is available for Windows 64-bit environments, and deploys and configures:

* The Splunk Distribution of the OpenTelemetry Collector for Windows

* Fluentd through the td-agent, which is deactivated by default

To install the package using the installer script, follow these steps:

1. Ensure that you have Administrator access on your host.

2. Run the following PowerShell command on your host, replacing the following variables for your environment:

* SPLUNK_REALM: This is the realm to send data to. The default is us0. See realms .

* SPLUNK_ACCESS_TOKEN: This is the base64-encoded access token for authenticating data ingest requests. Your access token needs to have the ingest authorization scope. See Create and manage organization access tokens using Splunk Observability Cloud.

```powershell
& {Set-ExecutionPolicy Bypass -Scope Process -Force; $script = ((New-Object System.Net.WebClient).DownloadString('https://dl.signalfx.com/splunk-otel-collector.ps1')); $params = @{access_token = "SPLUNK_ACCESS_TOKEN"; realm = "SPLUNK_REALM"}; Invoke-Command -ScriptBlock ([scriptblock]::Create(". {$script} $(&{$args} @params)"))}
```

If you need to activate TLS in PowerShell, use the command:

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
```
</windows-examples>

You must place commands in bash code blocks.
"""

UNINSTALL_SPLUNK_OTEL_COLLECTOR = """Provide the commands to completely uninstall the Splunk OpenTelemetry Collector from a standard Linux system, including removing configuration and data directories.
<output_format>Place commands in bash code blocks.</output_format>"""

# Add more specific prompts here, following the OPERATION_PRODUCT naming convention
# e.g., CONFIGURE_SPLUNK_OTEL_COLLECTOR = """..."""