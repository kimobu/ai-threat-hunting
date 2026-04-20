---
name: elastic-security-onion
description: Query the JHU CTIH Security Onion Elasticsearch instance at https://so-rest.jhu-ctih.training using ELASTIC_API_KEY authentication. Use when Codex needs to inspect Security Onion telemetry, run Elasticsearch DSL queries against logs-*, filter results by @timestamp, retrieve host, process, user, authentication, or network events, or export results for notebooks, labs, and investigations. The environment is primarily a Microsoft Windows Active Directory domain, but the skill should stay broadly useful across mixed host and network telemetry.
---

# Elastic Security Onion

## Overview

Use this skill to query the training Elasticsearch server without rebuilding the client each time. Prefer the bundled scripts for one-off retrieval, and import the client module only when a notebook or Python workflow needs a DataFrame directly.

## Quick Start

1. Ensure `ELASTIC_API_KEY` is set in the shell environment or stored in a `.env` file.
2. Run `scripts/query_elastic.py` for ad hoc searches.
3. Import `scripts/elastic_client.py` when the task needs a Polars DataFrame inside Python code.
4. Read [references/query-patterns.md](references/query-patterns.md) when building event-specific filters.

## Query Workflow

- Start with `index="logs-*"` unless the user explicitly names another index.
- Add `start_date` and `end_date` whenever the task has a time window. Keep the time filter in the helper instead of duplicating it inside the query unless the query needs a custom range clause.
- Build exact-match filters in `query.bool.filter` with `term` or `terms`.
- Keep the query body as plain Elasticsearch DSL. The client also accepts `elasticsearch_dsl` objects with `to_dict()`.
- Keep the projected field set small. The default fields match the course notebooks and cover common pivots across host, process, user, and network data.
- Export results when the next step needs a file artifact. Use `--format csv`, `--format json`, or `--format parquet`.

## Run One-Off Queries

Run a JSON string directly:

```bash
python3 scripts/query_elastic.py \
  --index logs-* \
  --query-json '{"query":{"bool":{"filter":[{"term":{"event.dataset":"esf"}},{"term":{"event.action":"exec"}}]}}}' \
  --start-date 2024-11-14T00:00:00Z \
  --end-date 2024-11-21T00:00:00Z
```

Run a query from a file and save it:

```bash
python3 scripts/query_elastic.py \
  --index logs-* \
  --query-file /tmp/network_query.json \
  --start-date 2024-11-20T00:00:00Z \
  --end-date 2024-11-21T00:00:00Z \
  --format csv \
  --output /tmp/network_hits.csv
```

Override the field projection when the task needs fewer or different columns:

```bash
python3 scripts/query_elastic.py \
  --index logs-* \
  --query-json '{"query":{"bool":{"filter":[{"term":{"host.name":"dc01.dundermifflin.local"}}]}}}' \
  --field @timestamp \
  --field host.name \
  --field process.name \
  --field process.command_line
```

## Import From Python

Import the client when a notebook or script needs a DataFrame:

```python
from pathlib import Path
import sys

skill_dir = Path("/Users/kimo/.codex/skills/elastic-security-onion")
sys.path.insert(0, str(skill_dir / "scripts"))

from elastic_client import ElasticQuery

client = ElasticQuery()
df = client.search(
    index="logs-*",
    query={
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event.dataset": "endpoint.events.network"}},
                    {"term": {"event.action": "connection_attempted"}},
                ]
            }
        }
    },
    start_date="2024-11-20T00:00:00Z",
    end_date="2024-11-21T00:00:00Z",
)
client.close()
```

## Operational Notes

- Expect TLS verification to be disabled for this training endpoint. Keep that behavior unless the environment changes.
- Expect the helper to return document hits, not aggregations. If the task is aggregation-heavy, extend the helper deliberately instead of forcing the tabular path.
- Clear the scroll context after retrieval. The bundled client already does this.
- Use the default field list unless the task clearly needs more. Small responses are easier to inspect and cheaper to move through notebooks and agent flows.
- Prefer UTC timestamps with a `Z` suffix.

## Resources

- Use `scripts/elastic_client.py` for the reusable Python client.
- Use `scripts/query_elastic.py` for command-line querying and exporting.
- Read [references/query-patterns.md](references/query-patterns.md) for common field filters and investigation patterns.
