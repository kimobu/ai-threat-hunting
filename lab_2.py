import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 0xc: Tool calling assistants
    In this notebook we turn an LLM into a triage assistant by giving it custom tools for enrichment and investigation.

    **Agenda**

    - Agents
    - Why tool calling matters
    - Building custom function tools
    - Using those tools during process triage
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Agents
    AI agents are LLM-driven programs that can make decisions and take actions, rather than just responding to prompts.

    We give the agent some guidance and let it make a plan, use tools, and maintain context to solve complex tasks autonomously.

    Instead of just generating text, the agent controls workflow execution.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tools

    |Type|Description|Examples|
    |----|-----------|--------|
    |Data|Enable agents to retrieve context and information necessary for executing the workflow|Query a SIEM, read PDF documents, or search the web.|
    |Action|Enable agents to interact with systems to take actions such as adding new information to databases, updating records, or sending messages|Send a message on Slack, update an investigation ticket, block a domain|
    |Orchestration|Agents themselves can serve as tools for other agents|Research agent, investigation agent|
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Making a tool

    - You define each tool manually in code
    - Tightly coupled: tools are hardcoded into the agent
    - LLM must be explicitly told about each tool's schema


    ```python
    def check_hash(hash: str) -> bool:
        ...

    tools = [check_hash]
    agent = Agent(tools=tools)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lab 0xc
    In this lab we are going to create AI agents that further investigate the results of the GPT Detector. The agents will:

    - Create queries to pull additional information from Elastic
    - Query threat intelligence sources to get additional information on indicators of compromise (IOC)

    To do this we will use the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

    Let's start with the agents hello world example.

    In this SDK we use `Agent` to create an agent. We can define the agent's instructions, what model it should use, and what tools it has access to.

    To run an agent, we use the `Runner` class. It can run asynchronously, synchronously, and streamed.

    Create an agent named "Poet" with simple instructions to on being a poetic macOS security analyst.

    Then, run the agent synchronously, asking it to write a poem about ESF. The `Runner` result contains a few items. Print the full results to see what they are.
    """)
    return


@app.cell
async def _():
    from agents import Agent, Runner

    _agent = Agent(name="Poet", instructions="You are a poetic macOS security analyst.")

    _result = await Runner.run(_agent, "Write a poem about ESF.")

    print(_result)
    return Agent, Runner


@app.cell
def _():
    import pathlib

    import polars as pl
    from dotenv import load_dotenv
    from utils.elastic import ElasticQuery

    load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parent / ".env")

    detections_path = pathlib.Path("data/gpt_detector_results.parquet")

    gpt_results = pl.read_parquet(detections_path)
    detections = gpt_results.filter(pl.col("risk_score") > 7)

    detections.head()
    return ElasticQuery, detections, load_dotenv


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SIEM Agent
    Now let's make an agent that interacts with our Elastic SIEM.

    For this agent, we'll use model `gpt-4.1`. Review the [gpt-4.1 prompting guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide).

    GPT 4.1 has a large context window of 1 million tokens. However, since the SIEM agent will interact with Elasticsearch and retrieve data, it's possible that the agent could go off the rails and collect too much data, exceeding the allowed number of tokens. We'll put a guardrail in place by ensuring we return at max 200 rows from any Elastic query.

    The OpenAI Agents SDK uses **local context** that can provide data or dependencies for tools. This is represented by a `RunContextWrapper` class. We will use this class to provide an instance of the `ElasticQuery` class to the agent for tool calls. We pass this into tool functions as the `wrapper` parameter, and we can then access its properties via `wrapper.context.<my_local_context>`.

    To give a tool to an agent, we annotate a Python function with the `@function_tool` decorator. You may need to set `strict_mode=false` to disable strict JSON schema. The Agents SDK will parse these decorated functions and provide the parameters and docstrings to the LLM to help it decide when to use the tool. We should use very descriptive names to help the LLM in this process. For example, instead of a generic tool name like `get_data` we might use `get_network_connections_by_process_ids`.

    LLMs operate on text* so we need to convert any tool call results into text. The `ElasticQuery.search` function returns a Dataframe. Just like we did in the GPT detector, we can use `to_pandas().to_markdown()` to convert the relevant Dataframe to plaintext.

    Create a function tool that will query Elastic. This function should take 2 parameters: wrapper and body. Wrapper is the local context providing access to the ElasticQuery context and body is a dictionary Elasticseach query that the LLM will make. The goal of this function is to retrieve network connections associated to processes that were flagged by the GPT detector.
    """)
    return


@app.cell
def _(ElasticQuery):
    import os
    import requests
    from agents import RunContextWrapper, function_tool
    from typing import Any

    class ElasticContext:
        def __init__(self):
            self.client = ElasticQuery()

    @function_tool(strict_mode=False)
    async def get_network_connections_by_process_ids(
        wrapper: RunContextWrapper[ElasticContext], 
        body: dict[str, Any],
    ) -> str:
        """
        Retrieve network connections from elasticsearch by querying for process ids.
        Args:
            body: a dictionary of elasticsearch "query", with "bool", "filter", etc and specific terms to search for.
        Returns:
            A markdown table of the hits.
        """
        fields = ["host.name", "user.name", "process.name", "process.pid", "source.ip", "source.port", "destination.ip", "destination.port"]
        results = wrapper.context.client.search(query=body, index="logs-*")
        if len(results) > 200:
            results = results.sample(n=200)
        return results.select(fields).to_pandas().to_markdown()

    return (
        ElasticContext,
        RunContextWrapper,
        function_tool,
        get_network_connections_by_process_ids,
        os,
        requests,
    )


@app.cell
def _():
    SIEM_INSTRUCTIONS = """
    # Role and objective
    You are an expert threat investigator who specializes in querying Elasticsearch for relevant data.
    You are an agent - please keep going until the userâs query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved.
    You have access to an Elasticsearch instance that contains telemetry from host and network based sensors. The Elasticsearch data conforms to Elastic Common Schema. You should use this tool to retrieve data that matches the user's request.

    # Instructions
    Given text from a user, decide what type of data is being asked for and create a valid Elasticsearch query.
    Some common data types their corresponding Elastic Common Schema fields:
    - network: source.ip, destination.ip, source.port, destination.port
    - hosts: host.name
    - users: user.name, user.title, user.department
    - processes: process.executable, process.pid, process.command_line
    - files: file.target
    - event: event.dataset, event.action, event.category

    Valid event.dataset values are: esf, endpoint.events.file, endpoint.events.network
    For esf data, valid event.action values are: creation, exec
    For esf data, valid event.category values are: "host,file", "host,process"
    For endpoint.events.file data, valid event.action values are: creation, deletion and the only valid event.category is file.
    For endpoint.events.network, valid event.action values are: connection_attempted, connection_accepted and the only valid event.category is network.

    Queries should be scoped to specific time frames. Datetimes are in UTC and formatted as strings like "2024-11-20T00:00:00Z". You should also scope queries by event.

    Here's an example of a valid query: {'query': {'bool': {'filter': [{'term': {'host.name': 'scr-office-imac.local'}}, {'term': {'event.category': 'host,process'}}, {'range': {'@timestamp': {'gte': '2024-11-21T00:00:00Z', 'lt': '2024-11-22T00:00:00Z'}}}]}}}

    You should return data as a table. Your query may not return many results; do not offer additional help. Do not make up results. Return only the information the user asked for. Do not provide explanations.

    # Examples
    <example1 type="get_network_connections_by_process_ids">
    <input>Find network connections from my_host_name with PID values of 1, 2, or 3 between June 1 and 4</input>
    Here you should look for "host.name" = "my_host_name", "event.category" = "process", "process.pid" in [1,2,3]
    Note that a valid query must have "query" as the top level key
    <output>
    |process.name|process.pid|source.ip|source.port|destination.ip|destination.port|
    </output>
    </example>

    Do NOT ask for confirmation. If the start and end times are the same, set start time to -15 minutes and end time to +15 minutes. If there are no network connections, simply state so.
    """
    return (SIEM_INSTRUCTIONS,)


@app.cell
def _(
    Agent,
    ElasticContext,
    SIEM_INSTRUCTIONS,
    get_network_connections_by_process_ids,
):
    elastic_context = ElasticContext()

    siem_agent = Agent(
        name="SIEM agent", 
        instructions=SIEM_INSTRUCTIONS, 
        tools=[get_network_connections_by_process_ids],
        model="gpt-5-mini"
    )
    return elastic_context, siem_agent


@app.cell
async def _(Runner, detections, elastic_context, siem_agent):
    grouped = detections.group_by(["host.name", "process.group_leader.pid"])
    for _group_key, _group_df in grouped:
        _host_name, _pgid = _group_key
        _start = _group_df['@timestamp'].min()
        _end = _group_df['@timestamp'].max()
        _pids = _group_df['process.pid'].to_list()
        _result = await Runner.run(siem_agent, f"Get network conenctions from host {_host_name} between {_start} and {_end} that have process IDs of {_pids}", context=elastic_context)
        print(_result.final_output)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Intel agent
    Let's make another agent that interacts with the Threat Fox database. Threat Fox is an abuse.ch service for sharing indicators of compromise associated with malware. We use the same Malware Bazaar API key.

    The API is documented here: https://threatfox.abuse.ch/api/#search-ioc

    First we'll create a ThreatFoxContext that does the following:

    - Load the .env file
    - Store the Threat Fox API URL
    - Set the `headers` dictionary we'll use to pass our API key

    Create another function tool that takes two parameters:

    - wrapper: the ThreatFoxContext context
    - ioc: a string that we'll search Threat Fox for (an IP address)

    The function will then use `requests` to search the Threat Fox API for any IP the LLM identifies.
    """)
    return


@app.cell
def _(RunContextWrapper, function_tool, load_dotenv, os, requests):
    class ThreatFoxContext:
        def __init__(self):
            load_dotenv()
            AUTH_KEY = os.getenv("MALWAREBAZAAR_API_KEY")
            self.url = "https://threatfox-api.abuse.ch/api/v1/"
            self.headers = {
                "Auth-Key": AUTH_KEY
            }

    @function_tool(strict_mode=False)
    async def get_threatfox_intel_by_ip_address(
        wrapper: RunContextWrapper[ThreatFoxContext], 
        ioc: str,
    ) -> str:
        """
        Retrieve threat intelligence enrichments on an IOC like an IP address from Threat Fox.
        Args:
            ioc: The IP address to query
        Returns:
            Intelligence about an IOC including a description, tags, and confidence
        """
        payload = {
            "query": "search_ioc",
            "search_term": ioc,
            "exact_match": False
        }

        response = requests.post(wrapper.context.url, headers=wrapper.context.headers, json=payload)
        results = response.json()
        return results.get("data", [])

    return ThreatFoxContext, get_threatfox_intel_by_ip_address


@app.cell
def _():
    INTEL_INSTRUCTIONS = """
    You are an expert threat investigator who focuses on enriching IOCs.
    You are an agent - please keep going until the userâs query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved.

    You have access to the Threat Fox API. This lets you lookup IOCs like IP addresses to retrieve threat intelligence.

    # Instructions
    Given user input, look for indicators of compromise that can be looked up.
    Use your tools to enrich the IOCs. You can only look up one IOC at a time.
    Summarize the threats and malware that associated with the IOC. Use the enrichment results to obtain this information. Only use the returned information. If nothing is returned, simply state that there is no enrichment available. 
    Include the confidence and any tags so that the user can make a well-informed decision about the threat level.

    # Examples
    <input>Here are some IP addresses to enrich: 1.1.1.1, 8.8.8.8</input>
    <output>IP address 1.1.1.1 has been seen activing as a botnet command&control server. It was used for the Cobalt Strike malware, which may also be known as Agentemis, BEACON, or CobaltStrike. The confidence level is 75 and the associated tags are [cobalstrike]
    """
    return (INTEL_INSTRUCTIONS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Just like the siem_agent, let's create the ThreatFoxContext and intel_agent.
    """)
    return


@app.cell
def _(
    Agent,
    INTEL_INSTRUCTIONS,
    ThreatFoxContext,
    get_threatfox_intel_by_ip_address,
):
    threatfox_context = ThreatFoxContext()

    intel_agent = Agent(
        name="Intel agent", 
        instructions=INTEL_INSTRUCTIONS, 
        tools=[get_threatfox_intel_by_ip_address],
        model="gpt-5-mini"
    )
    return intel_agent, threatfox_context


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's test the agent by asking it to lookup a couple of IP addresses:
    """)
    return


@app.cell
async def _(Runner, intel_agent, threatfox_context):
    _result = await Runner.run(intel_agent, f"Lookup these IP addresses: 74.48.192.2, 54.191.179.49", context=threatfox_context)
    print(_result.final_output)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reflection
    How did the tool-enabled assistant compare to a plain prompt?

    Which fields from Elastic and ThreatFox were most useful?

    What additional enrichment tools would make this assistant more reliable?
    """)
    return


if __name__ == "__main__":
    app.run()
