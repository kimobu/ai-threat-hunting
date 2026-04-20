# Query Patterns

Use this reference when building Elasticsearch DSL for the Security Onion server at `https://so-rest.jhu-ctih.training`.

The training environment is centered on Security Onion telemetry from a Windows-heavy enterprise, but these patterns should remain useful for mixed host and network investigations rather than assuming only Windows or only Active Directory data.

## Common Defaults

- Start with `index="logs-*"` unless a narrower index is known.
- Scope searches with `start_date` and `end_date` whenever possible.
- Use `query.bool.filter` for exact-match investigations.
- Project only the fields needed for the next step.

## Common ECS Fields

- Host pivots: `host.name`, `host.os.family`, `host.os.version`
- Process pivots: `process.name`, `process.pid`, `process.command_line`, `process.executable`
- Parent pivots: `process.parent.name`, `process.parent.pid`, `process.parent.executable`
- Network pivots: `source.ip`, `source.port`, `destination.ip`, `destination.port`, `network.protocol`
- User pivots: `user.name`, `user.department`, `user.title`
- Email pivots: `smtp.subject`, `smtp.from`, `smtp.to`
- Time: `@timestamp`

## Common Event Filters

Use these exact values when the task lines up with the available telemetry:

- `event.dataset = "esf"`
- `event.action = "exec"` for ESF process execution
- `event.action = "creation"` for ESF creation events
- `event.dataset = "endpoint.events.file"`
- `event.action = "creation"` or `event.action = "deletion"` for file activity
- `event.dataset = "endpoint.events.network"`
- `event.action = "connection_attempted"` or `event.action = "connection_accepted"` for network activity

## Example Queries

Filter for process execution events:

```json
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "event.dataset": "endpoint.events.process" } },
        { "term": { "event.action": "start" } }
      ]
    }
  }
}
```

Filter for network activity from one host:

```json
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "event.dataset": "endpoint.events.network" } },
        { "term": { "host.name": "ws-23.dundermifflin.local" } }
      ]
    }
  }
}
```

Filter for multiple process ids:

```json
{
  "query": {
    "bool": {
      "filter": [
        { "terms": { "process.pid": [1, 2, 3] } }
      ]
    }
  }
}
```

Filter for one executable path:

```json
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "process.executable": "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe" } }
      ]
    }
  }
}
```

## Notes

- Pass time windows through the client arguments unless the task needs a custom range clause inside the query body.
- Expect document retrieval. Do not assume the helper handles aggregation-only responses.
- Override the default field list with repeated `--field` flags when the task needs a custom projection.
