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
    # 0xd: Model Context Protocol and Agent Orchestration
    In this notebook we connect an assistant to tools exposed through an MCP server instead of defining every tool directly in Python.

    **Agenda**

    - MCP
    - Orchestrating agents
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # MCP
    **Model Context Protocol (MCP)** is a standardized interface that allows AI agents to use tools and access external data safely and flexibly.

    Think of MCP as a universal adapter between LLM agents and real-world systems:

    - Files
    - Documents
    - Databases
    - APIs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MCP Architecture
    ![](public/mcp.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MCP Tools

    - Agents (MCP host) use MCP client to connect to MCP server
    - Agent discovers available tools dynamically at runtime
    - Each tool is self-describing (name, input schema, output schema)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Agent tools vs MCP

    |Feature|Tools|MCP|
    |-------|-----|---|
    |Tool definition|"Hardcoded" in agent code|Hosted on server|
    |Discovery|Manual|Dynamic via protocol|
    |Scalability|Limited|Easily extensible|
    |Tool location|Local only|Local or remote|
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Agent Orchestration
    ## Patterns

    - **Single agent**: a single agent has all tools and uses a single prompt template
    - **Multi-agent manager**: a central manager agent calls other agents as tools. The manager agent returns text to the user.
    - **Multi-agent decentralized**: agents handoff workflows from one to another. The final called agent returns text to the user
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![](public/agent_patterns.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lab 0xd
    In this lab we'll create a new agent that can use MCP and orchestrate our agents so they act together to solve a larger problem.

    ## Model Context Protocol
    Lets create a model that uses MCP. The Agents SDK supports [providing MCP servers to agents](https://openai.github.io/openai-agents-python/mcp/).

    We'll use a local MCP server that connects to the Malware Bazaar API.

    First, you'll need to `git clone` this repository: https://github.com/mytechnotalent/MalwareBazaar_MCP

    /// admonition
    Follow the install instructions:
    ```
    cd MalwareBazaar_MCP
    uv init .
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```
    ///

    Next we'll use `MCPServerStdio` from the Agents SDK. The **stdio** transport means we will run the server as a subprocess of our application. The subprocess will be the malwarebazaar_mcp.py file.  This class takes a couple of parameters:

    - `name`: What we want to call the server
    - `params`: how to run the server:
        - `command`: we'll use `uv` to run the python file
        - `args`: a list of arguments to `uv`:
            - --directory
            - the path to where you cloned the git repo
            - run
            - malwarebazaar_mcp.py
    - `tool_filter`: a list of allowed or blocked tool names from the MCP server

    I think it's helpful to scope the agent to specific tools from this MCP server. Use `agents.mcp.create_static_tool_filter` and only allow the "get_taginfo" tool.

    /// admonition
    Copy your .env file to the MalwareBazaar_MCP server directory
    ///
    """)
    return


@app.cell
def _():
    import os
    import pathlib
    import shutil

    from agents import Agent, Runner
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parent / ".env")

    uv_path = shutil.which("uv") or "uv"
    malwarebazaar_mcp_dir = pathlib.Path.home() / "code" / "MalwareBazaar_MCP"

    print("uv path:", uv_path)
    print("MCP repo:", malwarebazaar_mcp_dir)
    return Agent, Runner, load_dotenv, malwarebazaar_mcp_dir, os, uv_path


@app.cell
async def _(malwarebazaar_mcp_dir, uv_path):
    from agents.mcp import MCPServerStdio, create_static_tool_filter

    mcp_server = MCPServerStdio(
        name="Malware Bazaar MCP Server",
        params={
            "command": uv_path,
            "args": [
                "--directory",
                str(malwarebazaar_mcp_dir),
                "run",
                "malwarebazaar_mcp.py",
            ],
        },
        tool_filter=create_static_tool_filter(allowed_tool_names=["get_taginfo"]),
    )
    await mcp_server.connect()
    return (mcp_server,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next make a lightweight set of instructions for our defender agent, and give it access to the MCP server.
    """)
    return


@app.cell
def _(Agent, mcp_server):
    DEFENDER_INSTRUCTIONS="""
    You are a helpful network defender. Your job is to retrieve malware hashes that will be blocked from executing.
    User tools to achieve the task. NEVER truncate the results. It is extremely important that we can block all malware.
    """

    defender_agent = Agent(
        name="Defender agent",
        instructions=DEFENDER_INSTRUCTIONS,
        mcp_servers=[mcp_server],
        model="gpt-5-mini",
    )
    return (defender_agent,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Do a quick test that the MCP server works with the agent. You should have about 23 hits.
    """)
    return


@app.cell
async def _(Runner, defender_agent):
    result = await Runner.run(defender_agent, "Get malware hashes tagged with DeimosC2")
    print(result.final_output)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orchestration
    We now have 3 agents that specialize in different steps of our incident response process.

    1. siem_agent: searches our SIEM for related network connections
    2. intel_agent: searches Threat Fox for information about IOCs
    3. defender_agent: gets related malware hashes that we could block or alert on

    Let's create 2 more agents:

    1. search_agent: Search the Internet for additional information on malware threats we found
    2. writer_agent: Takes all the information found and writes a report

    We'll also demonstrate using structured outputs in agents. Altogether, these agents are investigating the GPT detections. If you remember, the TP/FP rates were unbalanced and we don't want humans to investigate every detection. Instead, let's have these agents make a recommended action that is one of true_positive, false_positive, or benign so we can quickly action the detection.

    We'll incorporate the recommended action into an incident report. The report should consist of analysis of what happened, a list of C2 IPs that were found, a list of MITRE tags, a list of tags from Threat Fox, a list of related malware hashes, the infected host name, and the recommended action.

    Model both the recommended action and incident report as Pydantic models.
    """)
    return


@app.cell
def _():
    from enum import Enum
    from pydantic import BaseModel 

    class RecommendedAction(str, Enum):
        true_positive = "true_positive"
        false_positive = "false_positive"
        benign = "benign"

    class IncidentReport(BaseModel):
        analysis: str 
        c2: list[str]
        mitre_tags: list[str]
        abuse_tags: list[str]
        related_hashes: list[str]
        infected_host: str 
        recommended_action: RecommendedAction

    return (IncidentReport,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now make the search agent and writer agent.

    The search agent should be instructed to search the web for the given terms and produce a summary of about 300 words. It should focus on key malware and MITRE ATT&CK TTPs.

    From the Agents SDK, we can import the WebSearchTool and give that as a tool to the agent. We should set ModelSettings and tell the agent that a tool is required.

    The writer agent should be instructed to create an incident report. Tell the agent what fields should be in the report: each field from the IncidentReport pydantic model. Tell the agent that it needs to have factual data in its report and that some data might not exist. For example, there may not be a C2 associated with any of the processes we detected.

    Give the writer agent the search_agent as a tool.
    """)
    return


@app.cell
def _(Agent, IncidentReport):
    from agents import WebSearchTool, function_tool, RunContextWrapper
    from agents.model_settings import ModelSettings

    SEARCH_PROMPT = """
    You are research assistant specializing in cyber security incidents. Given a search term,
    use web search to retrieve up to date context on a cyber security threat and produce a short
    summary of at most 300 words. Focus on key malware and MITRE ATT&CK TTPs.
    """

    search_agent = Agent(
        name="Search agent", 
        instructions=SEARCH_PROMPT, 
        tools=[WebSearchTool()],
        model_settings=ModelSettings(tool_choice="required")
    )

    WRITER_PROMPT = """
    You are a senior threat analyst tasked with writing a cohesive report for a cyber security incident.
    You will be provided with the initial detection data and some additional research performed on IOCs.
    Your report must be grounded in what actually happened and a reference must be provided in-line for any claim.

    The report consists of the following fields:
    - Analysis: a crisp summary of what transpired and what the investigation found.
    - C2: a list of any domains or IP addresses found, empty if none
    - MITRE tags: a list of MITRE ATT&CK TTPs found, empty if none
    - abuse tags: a list of tags from the Threat Fox enrichment, empty if none
    - related hashes: a list of hashes from Malware Bazaar, empty if none
    - infected host: the host from the incident
    - recommended action: true positive, false positive, or benign

    # Instructions
    1. You should first come up with an outline for an incident report. 
    2. Then, generate the report and return that as your final output. 
    3. The final report should be in markdown format. 
    4. IOCs should be defanged like "https://evil.com" -> "hxxps://evil[.]com". 
    5. Do not make up any IOCs

    You have access to web search to find up to date context on the threat and to find the correct MITRE ATT&CK TTPs.
    """

    writer_agent = Agent(
        name="Report Agent", 
        instructions=WRITER_PROMPT, 
        model="gpt-5-mini", 
        output_type=IncidentReport, 
        tools=[
            search_agent.as_tool(tool_name="search_web", tool_description="Use this tool to find update to date context on threats and MITRE TTPs")
        ]
    )
    return RunContextWrapper, function_tool, writer_agent


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, lets orchestrate the activity via an IncidentManager class.

    The manager should have a method `run` that is the entrypoint to the workflow. This method should take 1 paramter: `query` which will be the request to triage the GPT detection. The `run` method should then do 4 things:

    1. Search Elastic for related data using siem_agent
    2. Search Threat Fox using intel_agent
    3. Search Malware Bazaar using defender_agent
    4. Write a report using writer_agent

    Each of those steps can be a standalone method in IncidentManager that simply calls `Runner.run(agent, query, context)`. The report writing method should take the results of siem_agent, intel_agent, and defender_agent.
    """)
    return


@app.cell
def _(
    IncidentReport,
    Runner,
    defender_agent,
    elastic_context,
    intel_agent,
    siem_agent,
    threatfox_context,
    writer_agent,
):
    class IncidentManager:
        """
        Orchestrates the incident workflow: search for related C2, threat enrichment, and pivoting.
        """

        def __init__(self) -> None:
            pass

        async def run(self, query: str) -> None:
            c2_results = await self._search_elastic(query)
            # Have to shim in a recent C2 IP since ThreatFox ages IOCs out
            c2_results = c2_results.replace("77.221.151.41", "185.11.61.84")
            threatfox_results = await self._search_threatfox(c2_results)
            related_hashes = await self._search_malwarebazaar(threatfox_results)
            report = await self._write_report(query, c2_results, threatfox_results, related_hashes)
            return report

        async def _search_elastic(self, query: str) -> str | None:
            _result = await Runner.run(siem_agent, query, context=elastic_context)
            return _result.final_output

        async def _search_threatfox(self, query: str) -> str | None:
            _result = await Runner.run(intel_agent, query, context=threatfox_context)
            return _result.final_output

        async def _search_malwarebazaar(self, query: str) -> str | None:
            _result = await Runner.run(defender_agent, query)
            return _result.final_output

        async def _write_report(self, query: str, c2_results: str, threatfox_results: str, related_hashes: str) -> IncidentReport:
            _input_data = f"The initial detection was found by analyzing suspicious commands and returned {query}. We may have discovered command and control: {c2_results}. If the C2 was found, it's enrichment includes: {threatfox_results}. These may be related malware hashes: {related_hashes}."
            _result = await Runner.run(writer_agent, _input_data)
            return _result.final_output_as(IncidentReport)

    return (IncidentManager,)


@app.cell
async def _(incident_manager):
    threat = await incident_manager._search_threatfox(query="""|    | host.name             | user.name     | process.name   |   process.pid | source.ip     |   source.port | destination.ip   |   destination.port |\n|---:|:----------------------|:--------------|:---------------|--------------:|:--------------|--------------:|:-----------------|-------------------:|\n|  0 | scr-office-imac.local | michael.scott | BrewApp        |         10957 | 192.168.1.120 |         58385 | 185.11.61.84    |                 80 |\n|  1 | scr-office-imac.local | michael.scott | BrewApp        |         10957 | 192.168.1.120 |         58385 | 185.11.61.84    |                 80 |"""
    )
    return (threat,)


@app.cell
def _(threat):
    threat
    return


@app.cell
async def _(IncidentManager):
    import polars as pl

    reports = []
    incident_manager = IncidentManager()

    gpt_results = pl.read_parquet("data/gpt_detector_results.parquet")
    detections = gpt_results.filter(pl.col("risk_score") > 7)
    grouped = detections.group_by(["host.name", "process.group_leader.pid"])

    for _group_key, _group_df in grouped:
        _host_name, _pgid = _group_key
        _start = _group_df['@timestamp'].min()
        _end = _group_df['@timestamp'].max()
        _pids = _group_df['process.pid'].to_list()
        _result = await incident_manager.run(f"Triage this detection that occurred from {_start} to {_end} on {_host_name} by finding network connections from the associated PIDs: {_pids}")
        reports.append(_result)
    return incident_manager, pl, reports


@app.cell
def _(pl, reports):
    df = pl.DataFrame([report.model_dump() for report in reports])
    df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reflection
    What changed when the tool moved from a handwritten Python function to MCP?

    Which parts of the setup were simpler, and which parts still required local engineering work?

    Where would MCP fit best in a defender workflow?
    """)
    return


@app.cell
def _(Agent, RunContextWrapper, function_tool):
    """
    SIEM agent
    """
    from typing import Any
    from utils.elastic import ElasticQuery

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

    elastic_context = ElasticContext()

    siem_agent = Agent(
        name="SIEM agent", 
        instructions=SIEM_INSTRUCTIONS, 
        tools=[get_network_connections_by_process_ids],
        model="gpt-5-mini"
    )
    return elastic_context, siem_agent


@app.cell
def _(Agent, RunContextWrapper, function_tool, load_dotenv, os):
    """
    Intel agent
    """
    import requests

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

    threatfox_context = ThreatFoxContext()

    intel_agent = Agent(
        name="Intel agent", 
        instructions=INTEL_INSTRUCTIONS, 
        tools=[get_threatfox_intel_by_ip_address],
        model="gpt-5-mini"
    )
    return intel_agent, threatfox_context


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
