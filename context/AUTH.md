This file documents the authentication telemetry available in Elastic.

Process data is labeled by `event.category:authentication`.

# General fields
- host.name: hostname of the computer where the auth event occurred
- user.name: the user who authenticated
- process.name: the process that performed the auth event
- process.id: the id of the process that performed the auth event

# Elastic Agent
endpoint.events.security

## Key fields
- process.entity_id: a globally unique ID for the process that performed the auth event


# Windows event logs
system.security

## Key fields
- source.ip: where the auth event came from
- source.domain: the hostname where the auth event came from

# Auditd
system.auth

## Key fields
- system.auth.ssh.method: the type of login, eg publickey
- source.ip: where the auth event came from


# Log on events
- event.dataset:endpoint.events.security and event.action:log_on
- event.dataset:system.auth and event.action:ssh_login
- event.dataset:system.security and event.action:logged-in