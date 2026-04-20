import logging
import os
import urllib3
from pathlib import Path
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import polars as pl
import copy

class ElasticQuery:
    def __init__(self, host: str = "https://so-rest.jhu-ctih.training", port: int = 443, log_level: int = 5):
        self.logger = logging.getLogger("ElasticQuery")
        self.logger.setLevel(log_level)
        if not self.logger.hasHandlers():
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        project_root = Path(__file__).resolve().parents[1]
        dotenv_path = project_root / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        api_key = os.getenv("ELASTIC_API_KEY")
        if not api_key:
            raise ValueError("ELASTIC_API_KEY not found in environment variables.")
        
        self.client = Elasticsearch(
            f"{host}:{port}",
            api_key=api_key,
            verify_certs=False,  # Disable TLS verification,
            ssl_show_warn=False, # Hide verify_certs warning
        )
        
        self.fields = [
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
        urllib3.disable_warnings()

    def search(self, index: str, query: dict, start_date: str | None = None, end_date: str | None = None, 
               scroll: str = "2m", batch_size: int = 10000) -> pl.DataFrame:
        # Support elasticsearch_dsl Q objects
        if hasattr(query, "to_dict"):
            query = query.to_dict()
        """
        Execute a search query with optional date range filtering and return results as a Polars DataFrame.

        Args:
            index (str): The index to query.
            query (dict): The query DSL.
            start_date (str): Start date for filtering (format: YYYY-MM-DDTHH:MM:SSZ).
            end_date (str): End date for filtering (format: YYYY-MM-DDTHH:MM:SSZ).
            scroll (str): Scroll time to keep the search context alive.
            batch_size (int): Number of hits to retrieve per batch.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the filtered results.
        """
        query = copy.deepcopy(query)  # work on a fresh copy to avoid mutating the original dict
        # Add date range filter if start_date and/or end_date are provided
        if start_date or end_date:
            date_range_filter = {"range": {"@timestamp": {}}}
            if start_date:
                date_range_filter["range"]["@timestamp"]["gte"] = start_date
            if end_date:
                date_range_filter["range"]["@timestamp"]["lte"] = end_date
            
            # Add the date range filter to the query
            if "query" not in query:
                query["query"] = {}
            if "bool" not in query["query"]:
                query["query"]["bool"] = {}
            if "filter" not in query["query"]["bool"]:
                query["query"]["bool"]["filter"] = []
            
            query["query"]["bool"]["filter"].append(date_range_filter)
        
        # Initiate the search with scrolling
        response = self.client.search(
            index=index,
            body=query,
            scroll=scroll,
            size=batch_size,
            source=self.fields  # Pre-filter fields
        )

        # Scroll ID and initial hits
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

        # Extract filtered source data
        data = [hit["_source"] for hit in hits]

        # Scroll through remaining results
        while len(hits) > 0:
            response = self.client.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            data.extend(hit["_source"] for hit in hits)

        # Clear the scroll context
        self.client.clear_scroll(scroll_id=scroll_id)

        # Flatten nested dictionaries into dot-noted flat dicts
        def flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        flat_data = [flatten_dict(record) for record in data]
        # Build DataFrame scanning all rows to infer correct column types
        return pl.from_dicts(flat_data, infer_schema_length=None)
    
    def close(self):
        """
        Close the Elasticsearch client connection.
        """
        self.client.close()


# Example usage
if __name__ == "__main__":
    host = "security-onion-server"  # Replace with your server's hostname/IP
    port = 9200
    index = "zeek-logs*"  # Replace with the relevant index
    query = {
        "query": {
            "match_all": {}
        }
    }
    start_date = "2024-12-01T00:00:00Z"
    end_date = "2024-12-15T23:59:59Z"

    # Initialize the ElasticQuery class
    elastic_query = ElasticQuery(host, port)

    try:
        # Execute a query and retrieve the results
        df = elastic_query.search(index=index, query=query, start_date=start_date, end_date=end_date)
        print(df.head())  # Display the first few rows
    finally:
        # Ensure the client connection is closed
        elastic_query.close()
