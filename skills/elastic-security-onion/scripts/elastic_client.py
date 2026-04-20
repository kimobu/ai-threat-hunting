#!/usr/bin/env python3
from __future__ import annotations

import copy
import logging
import os
from pathlib import Path
from typing import Any

import polars as pl
import urllib3
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

DEFAULT_URL = "https://so-rest.jhu-ctih.training:443"
DEFAULT_FIELDS = [
    "@timestamp",
    "host.name",
    "host.os.family",
    "host.os.version",
    "process.command_line",
    "process.executable",
    "process.name",
    "process.pid",
    "process.entity_id",
    "process.working_directory",
    "process.parent.executable",
    "process.parent.name",
    "process.parent.pid",
    "process.parent.original_pid",
    "process.group_leader.pid",
    "process.Ext.ancestry",
    "process.session_leader.pid",
    "process.macho.company",
    "source.ip",
    "source.port",
    "destination.ip",
    "destination.port",
    "network.protocol",
    "user.name",
    "user.department",
    "user.title",
    "user.geo.city_name",
    "user.geo.region_name",
]


def _flatten_dict(value: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    items: list[tuple[str, Any]] = []
    for key, item in value.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(item, dict):
            items.extend(_flatten_dict(item, parent_key=new_key, sep=sep).items())
            continue
        items.append((new_key, item))
    return dict(items)


def _load_api_key(env_file: str | os.PathLike[str] | None = None) -> str:
    if env_file:
        load_dotenv(dotenv_path=Path(env_file), override=False)
    else:
        load_dotenv(override=False)

    api_key = os.getenv("ELASTIC_API_KEY")
    if not api_key:
        raise ValueError("ELASTIC_API_KEY not found in environment variables or .env.")
    return api_key


class ElasticQuery:
    def __init__(
        self,
        url: str = DEFAULT_URL,
        *,
        env_file: str | os.PathLike[str] | None = None,
        fields: list[str] | None = None,
        log_level: int = logging.WARNING,
    ) -> None:
        self.logger = logging.getLogger("ElasticQuery")
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            self.logger.addHandler(handler)

        urllib3.disable_warnings()
        self.fields = list(fields or DEFAULT_FIELDS)
        self.client = Elasticsearch(
            url,
            api_key=_load_api_key(env_file),
            verify_certs=False,
            ssl_show_warn=False,
        )

    def search(
        self,
        *,
        index: str,
        query: dict[str, Any] | Any,
        start_date: str | None = None,
        end_date: str | None = None,
        scroll: str = "2m",
        batch_size: int = 10000,
        fields: list[str] | None = None,
    ) -> pl.DataFrame:
        if hasattr(query, "to_dict"):
            query = query.to_dict()

        request_body = copy.deepcopy(query)
        if start_date or end_date:
            date_range_filter: dict[str, Any] = {"range": {"@timestamp": {}}}
            if start_date:
                date_range_filter["range"]["@timestamp"]["gte"] = start_date
            if end_date:
                date_range_filter["range"]["@timestamp"]["lte"] = end_date

            existing_query = request_body.get("query")
            if existing_query is None:
                request_body["query"] = {"bool": {"filter": [date_range_filter]}}
            elif "bool" in existing_query and isinstance(existing_query["bool"], dict):
                existing_query["bool"].setdefault("filter", [])
                existing_query["bool"]["filter"].append(date_range_filter)
            else:
                request_body["query"] = {
                    "bool": {
                        "must": [existing_query],
                        "filter": [date_range_filter],
                    }
                }

        response = self.client.search(
            index=index,
            body=request_body,
            scroll=scroll,
            size=batch_size,
            source=fields or self.fields,
        )

        scroll_id = response.get("_scroll_id")
        hits = response["hits"]["hits"]
        data = [hit.get("_source", {}) for hit in hits]

        try:
            while hits:
                response = self.client.scroll(scroll_id=scroll_id, scroll=scroll)
                scroll_id = response.get("_scroll_id")
                hits = response["hits"]["hits"]
                data.extend(hit.get("_source", {}) for hit in hits)
        finally:
            if scroll_id:
                self.client.clear_scroll(scroll_id=scroll_id)

        flat_data = [_flatten_dict(record) for record in data]
        return pl.from_dicts(flat_data, infer_schema_length=None)

    def close(self) -> None:
        self.client.close()
