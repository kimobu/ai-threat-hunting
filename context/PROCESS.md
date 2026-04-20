This file documents the process telemetry available in Elastic.

Process data is labeled by `event.category:process`.

# General fields
- host.name: hostname of the computer where process action occurred

# Elastic Agent
event.dataset:
- endpoint.events.process

## Key fields
- process.command_line: the command executed and its arguments
- process.entity_id: a globally unique ID for the process. May be more robust than PID
- process.Ext.ancestry: a list of ancestor entity_ids
- process.executable: the path to the program executed
- process.pid: the process id
- process.parent.pid: the parent process id
- process.parent.command_line: the parent process command line and its arguments
- user.name: who executed the process

# Powershell
event.datasets:
- windows.powershell
- windows.powershell_operational

## Key fields
- powershell.file.script_block_text: The powershell script executed

# Sysmon
event.dataset:
- windows.sysmon_operational

## Key fields
- process.hash.sha256: the sha256 of the program
- process.pe.original_file_name: metadata from the PE
- registry.path: path to a registry edit
- registry.key: registry key name
- registry.value: value set to a registry k ey


# Process creation
- event.dataset:sysmon_operational and event.action:"Process creation"
- event.dataset:endpoint.events.process and event.action:"start" (Windows)
- event.dataset:endpoint.events.process and event.action:"exec" (Linux, Mac)
- event.dataset:windows.sysmon_operational and event.action:"CreateRemoteThread" (DLL injection)
- event.dataset:windows.powershell_operational and event.action:"Execute a Remote Command"

# Registry edits
- event.dataset:windows.sysmon_operational and event.code:13