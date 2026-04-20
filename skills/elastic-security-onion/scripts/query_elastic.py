#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from elastic_client import ElasticQuery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the JHU CTIH Security Onion Elasticsearch server."
    )
    parser.add_argument("--index", required=True, help="Elasticsearch index pattern, such as logs-*.")
    parser.add_argument("--query-json", help="Inline Elasticsearch query DSL JSON.")
    parser.add_argument("--query-file", help="Path to a JSON file containing Elasticsearch query DSL.")
    parser.add_argument("--start-date", help="UTC start time, such as 2024-11-20T00:00:00Z.")
    parser.add_argument("--end-date", help="UTC end time, such as 2024-11-21T00:00:00Z.")
    parser.add_argument("--scroll", default="2m", help="Scroll keepalive window. Default: 2m.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10000,
        help="Documents to retrieve per batch. Default: 10000.",
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="Projected field. Repeat to override the default field list.",
    )
    parser.add_argument("--env-file", help="Optional .env file path containing ELASTIC_API_KEY.")
    parser.add_argument(
        "--format",
        choices=("table", "json", "csv", "parquet"),
        default="table",
        help="Output format. Default: table.",
    )
    parser.add_argument("--output", help="Optional output path for json, csv, or parquet.")
    return parser.parse_args()


def load_query(args: argparse.Namespace) -> dict[str, Any]:
    if args.query_json and args.query_file:
        raise ValueError("Pass either --query-json or --query-file, not both.")

    if args.query_file:
        return json.loads(Path(args.query_file).read_text())

    if args.query_json:
        return json.loads(args.query_json)

    return {"query": {"match_all": {}}}


def write_output(fmt: str, output: str | None, rows: list[dict[str, Any]], frame_repr: str) -> None:
    if fmt == "table":
        if output:
            Path(output).write_text(frame_repr + "\n")
        else:
            print(frame_repr)
        return

    if fmt == "json":
        payload = json.dumps(rows, indent=2, default=str)
        if output:
            Path(output).write_text(payload + "\n")
        else:
            print(payload)
        return

    raise ValueError(f"Unsupported write mode in write_output: {fmt}")


def main() -> int:
    args = parse_args()
    query = load_query(args)

    client = ElasticQuery(env_file=args.env_file, fields=args.field or None)
    try:
        df = client.search(
            index=args.index,
            query=query,
            start_date=args.start_date,
            end_date=args.end_date,
            scroll=args.scroll,
            batch_size=args.batch_size,
            fields=args.field or None,
        )
    finally:
        client.close()

    if args.format == "csv":
        if args.output:
            df.write_csv(args.output)
        else:
            print(df.write_csv())
        return 0

    if args.format == "parquet":
        if not args.output:
            raise ValueError("--output is required when --format parquet is used.")
        df.write_parquet(args.output)
        return 0

    write_output(args.format, args.output, df.to_dicts(), repr(df))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
