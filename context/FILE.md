This file documents the file telemetry available in Elastic.

Process data is labeled by `event.category:file`.

# General fields
- host.name: hostname of the computer where the file event occurred
- file.name: the file name
- file.path: the path to the file
- process.pid: the process that performed the file action
- user.name: the user that performed the file action

# Elastic Agent
event.dataset:endpoint.events.file

## Key fields
- process.entity_id: a globally unique identifier for the process that performed the file action


# Sysmon
event.dataset:windows.sysmon_operational


# File creation
- event.dataset:endpoint.events.file and event.action:creation
- event.dataset:windows.sysmon_operational and event.action:FileCreate

# File modification
- event.dataset:endpoint.events.file and event.action:rename
- event.dataset:endpoint.events.file and event.action:modification
- event.dataset:endpoint.events.file and event.action:overwrite
- event.dataset:windows.sysmon_operational and event.code:2 (timestomp)

# File deletion
- event.dataset:endpoint.events.file and event.action:deletion