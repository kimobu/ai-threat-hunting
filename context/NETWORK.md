This file documents the network telemetry available in Elastic.

Network data is labeled via `event.category:network`

# General fields
- destination.ip: destination IP address
- destination.port: destination port
- source.ip: source IP address
- source.port: source port

# Zeek
The majority of the network telemetry comes from Zeek. event.datasets:

- zeek.conn
- zeek.dns
- zeek.ssl
- zeek.dce_rpc
- zeek.kerberos
- zeek.file
- zeek.http
- zeek.smb_mapping
- zeek.notice
- zeek.weird
- zeek.smb_files
- zeek.stun
- zeek.x509
- zeek.smtp
- zeek.ntlm
- zeek.zeek
- zeek.dhcp
- zeek.software
- zeek.stun_nat
- zeek.dpd
- zeek.pe
- zeek.ssh
- zeek.tunnel
- zeek.rdp

## Key fields
- dns.query.name: hostname queried
- log.id.uid: a unique identifier for the connecction. Use to link the same connection across zeek datasets
- network.bytes: size of the connection
- network.protocol: application layer protocol

# Sysmon
event.dataset:
- windows.sysmon_operational

## Key fields
- dns.question.name: hostname queried
- dns.answers.data: IP address resolved
- host.name: the hostname that performed the network activity
- user.name: the user that performed the network activity
- process.pid: the process that performed the network action
- process.name: the process that performed the network action

# Elastic agent
event.dataset:
- endpoint.events.network

## Key fields
- host.name: the hostname that performed the network activity
- user.name: the user that performed the network activity
- process.entity_id: a globally unique identifier for the process that performed the network action
- process.pid: the process that performed the network action
- process.name: the process that performed the network action

# DNS events
- event.dataset:endpoint.events.network and event.action:lookup_requested or lookup_result
- event.dataset:sysmon_operational and event.action:"DNSEvent (DNS query)"

# Connection events
- event.dataset:endpoint.events.network and event.action:connection_attempted (outbound)
- event.dataset:endpoint.events.network and event.action:connection_accepted (inbound)
- event.dataset:windows.sysmon_operational and event.action:"Network connection"
- event.dataset:windows.sysmon_operational and event.action:"PipeEvent (Pipe Connected)"
- event.dataset:windows.sysmon_operational and event.action:"PipeEvent (Pipe Created)"