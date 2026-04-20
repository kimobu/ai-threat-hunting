import marimo

__generated_with = "0.23.1"
app = marimo.App(width="full")


@app.cell
def _(mo):
    mo.md(r"""
    # 0xb GPT Detector
    In this module we'll combine knowledge about macOS processes with LLMs to create a detector.

    **Agenda**:

    - GPT as a detector
    - Context
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # GPT as a detector
    Processes and command line activity are more or less a language and they are represented as text.

    Since LLMs excel at working with text we can use them to detect processes doing bad things.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## GPT detector vs traditional detections

    |Aspect|Traditional detections|GPT|
    |------|----------------------|---|
    |**Approach**|Hand-crafted rules or queries|LLM analyzes command sequences and classifies behavior|
    |**Expertise required**|Deep knowledge of attacker TTPs, query languages, and data schemas|Prompt engineering and understanding of LLM strengths/limitations|
    |**Flexibility**|Rigid: only catches things you knew to detect|Adaptive: can spot new/obfuscated tactics via semantic patterns|
    |**Maintenance**|High churn; update rules more often|Lower churn; refine prompts|
    |**Cost**|Low compute cost, high human cost|High compute cost, lower human cost|
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## GPT detector vs vector distance
    The anomaly-detection models we built in 0x9 found deviations in a user's normal activity.

    | Aspect | TF-IDF | GPT |
    |--------|--------|-----|
    |**Goal**    |Detect anomalies in command line activity per user | Detect suspicious or malicious behavior based on semantic understanding|
    |**How**     |Unsupervised anomaly detection|Semantic classification using natural language understanding|
    |**Context awareness**|Local to the user|Global to what we know is malicious|
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Globally malicious?
    ![](public/model_header.png)
    ![](public/model_knowledge_cutoff.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Training knowledge 1
    ![](public/alden_blog.png)
    [Revisiting Lazarus' Operation Intercept](https://alden.io/posts/revisiting-operation-intercept/)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Training knowledge 2
    ![](public/attack.png)
    [macOS Matrix](https://attack.mitre.org/matrices/enterprise/macos/)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## LLM foot guns
    Since LLMs are probabilistically predicting the next token, there are some weaknesses we need to be aware of:

    - **Regurgitation**: Memorizing high frequency or unique passages and repeating verbatim
    - **Bias**: Statistical patterns can amplify certain associations, leading to overgeneralization
    - **Hallucination**: Overconfidence in learned correlations leads to fabricated content
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Context
    ~~Attention~~ Context is all you need

    ![](public/context_engineering.png)

    Through prompt engineering and context management, we can mitigate some of the LLM foot guns. What information should we give to an LLM for it to effectively detect threats?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Identity section
    <img src="public/bot_identity.png"  style="float:right; width: 30%; height:100%" />
    Identity section describes purpose, communication style, goals

    - Who does GPT work for?
    - What is the LLM supposed to do?
    - Why is the LLM doing this?
    - Should we use bullet points, technical jargon, etc?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Instructions section
    Instructions section provide guidance on how to generate the response

    - Think about how you would determine if a command line is suspicious or not
    - Tell GPT what data will be provided and label the data
    - Do you want tags applied to what was found?
    - What should the output be? Boolean alert, paragraph analysis?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Examples section
    Examples section provides possible inputs and desired outputs

    - Provide an example of what the input data will look like
    - Provide an example of what the output should look like
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Context section
    Context section provides additional information like private/proprietary info

    - Inject additional information into the prompt to "enrich" the data
    - Who is the user and what do they do?
    - Add additional process information like parent, grand parent, siblings
    - Known false positives or things that should always be considered bad
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Who is the user and what do they do?
    The vector distance models we used built baselines and found outlier commands. We could use summarized outputs of those models, but we can also use the natural language abilities of LLMs to describe job roles.

    - This user is a software developer; their job responsibilities include...
    - This user is a recruiter; they often open PDFs and Word documents...
    - Use position descriptions, role guidelines, etc where possible
    - Can/should we build user dossiers on what we see them do?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Add additional process information

    - Leverage the process group ID to collect related processes.
    - Order processes by lineage
    - Include working directories, process names, and process identifiers
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Filter common processes
    Recurring background tasks like `medianalysisd` or `mdworker` are not likely to be meaningful.

    They will eat up tokens, wasting money and energy.

    Filter them out up front.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Determine how you want to run the detector
    Like all cybersecurity measures, there are tradeoffs.

    - How do we get the best context (streaming vs batch)
    - How often should we do a batch? How long do we want to let a potential adversary go unnoticed?
    - What kind of model do we want to use? Reasoning, general purpose?
        - Cost, compute time, and context window
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lab 0xb
    In this lab we'll build a GPT-based detector to find malicious processes. We will continue to use the Elastic Query client to pull data. Instead of building baselines and finding outlier commands, we'll build up the LLM prompt and package process information to send to the LLM.

    ## Acquire data
    Since we do not need to build a baseline, let's start by pulling Elastic data from the following time frames:

    - start_date: "2024-11-15T00:00:00Z"
    - end_date: "2024-11-21T00:00:00Z"

    We will also proactively filter out the hidden/system users by excluding user names that start with "_".

    Save these results as `process_df`.
    """)
    return


@app.cell
def _():
    from utils.elastic import ElasticQuery
    import polars as pl

    start_date = "2024-11-20T00:00:00Z"
    end_date = "2024-11-22T00:00:00Z"

    eq_client = ElasticQuery()

    esf_exec_filter = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event.dataset": "esf"}},
                    {"term": {"event.action": "exec"}}
                ],
                "must_not": [
                    {"prefix": {"user.name": "_"}}
                ]
            }
        }
    }

    process_df = eq_client.search(index="logs-*", query=esf_exec_filter, start_date=start_date, end_date=end_date)
    return end_date, eq_client, pl, process_df, start_date


@app.cell
def _(process_df):
    process_df
    return


@app.cell
def _(pl, process_df):
    process_df.group_by("user.name").agg(
        pl.col("process.executable").count().alias("unique_executable_count")
    ).sort("unique_executable_count", descending=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Filter common processes
    Let's inspect our process data more closely to find out what common processes we have.

    First we can see that there are almost 29,000 records:
    """)
    return


@app.cell
def _(process_df):
    process_df.count()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now if we group by the user and the process executable we can see that some executables like `mediaanalysisd` and `mdworker` do show up a lot. By filtering this out we can save on API costs and how long it takes to look through each user's activity.
    """)
    return


@app.cell
def _(pl, process_df):
    (process_df
        .group_by(["user.name", "process.executable"])
        .agg(pl.count().alias("count"))
        .sort(["user.name", "count"], descending=[False, True])
        .group_by("user.name")
        .head(5)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's remove the `mediaanalysisd` and `mdworker` entries, and also remove Google Chrome entries that are in the known-good location.
    """)
    return


@app.cell
def _(pl, process_df):
    excluded_exact = [
    "/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/Metadata.framework/Versions/A/Support/mdworker_shared",
    "/System/Library/PrivateFrameworks/MediaAnalysis.framework/Versions/A/mediaanalysisd"
    ]

    pattern_google_updater = r"^/Users/.*/Library/Application Support/Google/GoogleUpdater/.*/GoogleUpdater\.app/"

    process_df_filtered = process_df.filter(
        ~(
            pl.col("process.executable").is_in(excluded_exact) |
            pl.col("process.executable").str.contains(pattern_google_updater)
        )
    )
    return (process_df_filtered,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, let's retrieve information about our users.

    In our company, user information is stored in Microsoft Active Directory and that data gets sent to the Elastic SIEM. This data uses Windows event code 8000, so we'll query for that and store the results in `user_df`.

    From the `user_df` we really only need to keep the user's name, department, title, city, and region.

    /// attention |
    Your real company probably has this type of data somewhere, whether in AD, Workday, Slack, or some other system. Think of how you'd pull this information.
    ///
    """)
    return


@app.cell
def _(user_df):
    user_df
    return


@app.cell
def _(end_date, eq_client, start_date):
    user_info_filter = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event.code": "8000"}}
                ]
            }
        }
    }

    user_df = eq_client.search(index="logs-*", query=user_info_filter, start_date=start_date, end_date=end_date)
    user_df = user_df.unique(subset=["user.name"])
    return (user_df,)


@app.cell
def _(user_df):
    user_df_filtered = user_df.select(["user.name", "user.department", "user.title", "user.geo.city_name", "user.geo.region_name"])
    user_df_filtered
    return (user_df_filtered,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, let's merge the process and user dataframes together, joining on the `user.name` value.

    /// admonition
    Depending on your real company's SIEM, you could do this join earlier via SQL, SPL, ES|QL, etc
    ///
    """)
    return


@app.cell
def _(process_df_filtered, user_df_filtered):
    merged_df = user_df_filtered.join(process_df_filtered, on="user.name", how="inner")
    return (merged_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we want to group by process group ID so we can easily collect all of the related processes. We'll also need to group by the computer on which the PGID was found so that we do not mix processes from different computers. Let's take a look at what this data looks like so we can see what type of data we're going to send to the LLM.

    Using some example values for `host.name` and `process.group_leader.pid`, we show what a group will look like. Inside of the grouped processes, which all belong to the same process group, we'll collect the process IDs, parent process IDs, the parent process name, the process command line, and information about the user. By sorting on the timestamp and PID values, we make sure that the process execution chain order is retained.
    """)
    return


@app.cell
def _(merged_df, mo, pl):
    hostname = "scr-it-mac.local"
    group_pid = 12416

    _test_group = merged_df.filter(
        (pl.col("host.name") == hostname) &
        (pl.col("process.group_leader.pid") == group_pid)
    )

    _process_data = _test_group.sort("@timestamp", "process.pid").select(
        ["@timestamp", "process.pid", "process.parent.pid", "process.parent.name", "process.command_line", "user.name", "user.department", "user.title"]
    ).to_pandas().to_markdown()

    mo.md(_process_data)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With the data ready, let's build our GPT detector. The first thing to do is build our system/developer prompt. Provide the identity, instruction, and example sections. We'll dynamically add in the context section when we send the API request.
    """)
    return


@app.cell
def _():
    system_prompt = """
    <IDENTITY>
    You are a cyber security analyst at Dunder Mifflin paper company. You specialize in analyzing process execution from macOS endpoints. Your goal is to identify command line activity that indicates malicious activity and surface it to a human for review. You should use a clinical tone that explains the facts in a clear and concise manner and avoid jumping to conclusions unless there is overwhelming evidence.
    </IDENTITY>

    <INSTRUCTIONS>
    You will be given data about process execution that comes from Apple's Endpoint Security Framework that has been collected via the Elastic Agent and transformed into Elastic Common Schema. The process data will be in table format, and it represents all processes from a specific process group. The process information is ordered by time and indicates the order in which the processes occurred. You will be provided with the process ID, parent process ID, parent process name, the working directory of the process, and the process command line. You will also be given information about the host that the processes executed on and the name, department, and title about the user who executed the commands.

    To determine if the activity is malicious, consider the following factors:
    - What was the intent of the processes? 
    - Does that intent map to any known MITRE ATT&CK TTPs?
    - Does the process activity make sense given the user and their role?
    - When did the activity occur (all times are in UTC)? Was it inside normal working hours?

    Your output should consist of a risk score from 1-10, with 1 being very benign and 10 being very malicious. You should also provide a short description of what the processes did and why you assigned the score you did.
    </INSTRUCTIONS>

    <EXAMPLES>
    - New applications asking for passwords to decrypt the keychain: risk score 10, a common information stealing malware pattern.
    - Users using curl to retrieve a script from a webserver and piping to bash: risk score 5, could be legitimate but we need to investigate the script and webserver.
    - Creating new files in the LaunchAgents or LaunchDaemons directory: risk score 8, this could be malware persistence but we need to investigate the persisted file
    </EXAMPLES>

    """
    system_prompt_example = "IiIiCjxJREVOVElUWT4KWW91IGFyZSBhIGN5YmVyIHNlY3VyaXR5IGFuYWx5c3QgYXQgRHVuZGVyIE1pZmZsaW4gcGFwZXIgY29tcGFueS4gWW91IHNwZWNpYWxpemUgaW4gYW5hbHl6aW5nIHByb2Nlc3MgZXhlY3V0aW9uIGZyb20gbWFjT1MgZW5kcG9pbnRzLiBZb3VyIGdvYWwgaXMgdG8gaWRlbnRpZnkgY29tbWFuZCBsaW5lIGFjdGl2aXR5IHRoYXQgaW5kaWNhdGVzIG1hbGljaW91cyBhY3Rpdml0eSBhbmQgc3VyZmFjZSBpdCB0byBhIGh1bWFuIGZvciByZXZpZXcuIFlvdSBzaG91bGQgdXNlIGEgY2xpbmljYWwgdG9uZSB0aGF0IGV4cGxhaW5zIHRoZSBmYWN0cyBpbiBhIGNsZWFyIGFuZCBjb25jaXNlIG1hbm5lciBhbmQgYXZvaWQganVtcGluZyB0byBjb25jbHVzaW9ucyB1bmxlc3MgdGhlcmUgaXMgb3ZlcndoZWxtaW5nIGV2aWRlbmNlLgo8L0lERU5USVRZPgoKPElOU1RSVUNUSU9OUz4KWW91IHdpbGwgYmUgZ2l2ZW4gZGF0YSBhYm91dCBwcm9jZXNzIGV4ZWN1dGlvbiB0aGF0IGNvbWVzIGZyb20gQXBwbGUncyBFbmRwb2ludCBTZWN1cml0eSBGcmFtZXdvcmsgdGhhdCBoYXMgYmVlbiBjb2xsZWN0ZWQgdmlhIHRoZSBFbGFzdGljIEFnZW50IGFuZCB0cmFuc2Zvcm1lZCBpbnRvIEVsYXN0aWMgQ29tbW9uIFNjaGVtYS4gVGhlIHByb2Nlc3MgZGF0YSB3aWxsIGJlIGluIHRhYmxlIGZvcm1hdCwgYW5kIGl0IHJlcHJlc2VudHMgYWxsIHByb2Nlc3NlcyBmcm9tIGEgc3BlY2lmaWMgcHJvY2VzcyBncm91cC4gVGhlIHByb2Nlc3MgaW5mb3JtYXRpb24gaXMgb3JkZXJlZCBieSB0aW1lIGFuZCBpbmRpY2F0ZXMgdGhlIG9yZGVyIGluIHdoaWNoIHRoZSBwcm9jZXNzZXMgb2NjdXJyZWQuIFlvdSB3aWxsIGJlIHByb3ZpZGVkIHdpdGggdGhlIHByb2Nlc3MgSUQsIHBhcmVudCBwcm9jZXNzIElELCBwYXJlbnQgcHJvY2VzcyBuYW1lLCB0aGUgd29ya2luZyBkaXJlY3Rvcnkgb2YgdGhlIHByb2Nlc3MsIGFuZCB0aGUgcHJvY2VzcyBjb21tYW5kIGxpbmUuIFlvdSB3aWxsIGFsc28gYmUgZ2l2ZW4gaW5mb3JtYXRpb24gYWJvdXQgdGhlIGhvc3QgdGhhdCB0aGUgcHJvY2Vzc2VzIGV4ZWN1dGVkIG9uIGFuZCB0aGUgbmFtZSwgZGVwYXJ0bWVudCwgYW5kIHRpdGxlIGFib3V0IHRoZSB1c2VyIHdobyBleGVjdXRlZCB0aGUgY29tbWFuZHMuCgpUbyBkZXRlcm1pbmUgaWYgdGhlIGFjdGl2aXR5IGlzIG1hbGljaW91cywgY29uc2lkZXIgdGhlIGZvbGxvd2luZyBmYWN0b3JzOgotIFdoYXQgd2FzIHRoZSBpbnRlbnQgb2YgdGhlIHByb2Nlc3Nlcz8gCi0gRG9lcyB0aGF0IGludGVudCBtYXAgdG8gYW55IGtub3duIE1JVFJFIEFUVCZDSyBUVFBzPwotIERvZXMgdGhlIHByb2Nlc3MgYWN0aXZpdHkgbWFrZSBzZW5zZSBnaXZlbiB0aGUgdXNlciBhbmQgdGhlaXIgcm9sZT8KLSBXaGVuIGRpZCB0aGUgYWN0aXZpdHkgb2NjdXIgKGFsbCB0aW1lcyBhcmUgaW4gVVRDKT8gV2FzIGl0IGluc2lkZSBub3JtYWwgd29ya2luZyBob3Vycz8KCllvdXIgb3V0cHV0IHNob3VsZCBjb25zaXN0IG9mIGEgcmlzayBzY29yZSBmcm9tIDEtMTAsIHdpdGggMSBiZWluZyB2ZXJ5IGJlbmlnbiBhbmQgMTAgYmVpbmcgdmVyeSBtYWxpY2lvdXMuIFlvdSBzaG91bGQgYWxzbyBwcm92aWRlIGEgc2hvcnQgZGVzY3JpcHRpb24gb2Ygd2hhdCB0aGUgcHJvY2Vzc2VzIGRpZCBhbmQgd2h5IHlvdSBhc3NpZ25lZCB0aGUgc2NvcmUgeW91IGRpZC4KPC9JTlNUUlVDVElPTlM+Cgo8RVhBTVBMRVM+Ci0gTmV3IGFwcGxpY2F0aW9ucyBhc2tpbmcgZm9yIHBhc3N3b3JkcyB0byBkZWNyeXB0IHRoZSBrZXljaGFpbjogcmlzayBzY29yZSAxMCwgYSBjb21tb24gaW5mb3JtYXRpb24gc3RlYWxpbmcgbWFsd2FyZSBwYXR0ZXJuLgotIFVzZXJzIHVzaW5nIGN1cmwgdG8gcmV0cmlldmUgYSBzY3JpcHQgZnJvbSBhIHdlYnNlcnZlciBhbmQgcGlwaW5nIHRvIGJhc2g6IHJpc2sgc2NvcmUgNSwgY291bGQgYmUgbGVnaXRpbWF0ZSBidXQgd2UgbmVlZCB0byBpbnZlc3RpZ2F0ZSB0aGUgc2NyaXB0IGFuZCB3ZWJzZXJ2ZXIuCi0gQ3JlYXRpbmcgbmV3IGZpbGVzIGluIHRoZSBMYXVuY2hBZ2VudHMgb3IgTGF1bmNoRGFlbW9ucyBkaXJlY3Rvcnk6IHJpc2sgc2NvcmUgOCwgdGhpcyBjb3VsZCBiZSBtYWx3YXJlIHBlcnNpc3RlbmNlIGJ1dCB3ZSBuZWVkIHRvIGludmVzdGlnYXRlIHRoZSBwZXJzaXN0ZWQgZmlsZQo8L0VYQU1QTEVTPgoKIiIi"
    return (system_prompt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's create a GPT class that exposes a function we can call that will create the completion request. We'll use the AsyncOpenAI class so we can submit mulitple requests at a time.

    Implement the function `analyze`. This function takes a `input_df` as an argument, which is a Polars dataframe that contains commands we want analyzed. Fill in the missing `user_context` and `host_context` fields so that you provide the relevant context to the LLM.
    """)
    return


@app.cell
def _(RiskEvent, pl, system_prompt):
    from openai import AsyncOpenAI
    from dotenv import load_dotenv
    from pathlib import Path
    from tqdm import tqdm

    import asyncio
    import backoff
    import logging
    import openai
    import os

    class GPT:
        def __init__(self, log_level: int = logging.INFO, model: str = "gpt-5-mini"):
            self.logger = logging.getLogger("GPT")
            self.logger.setLevel(log_level)
            if not self.logger.hasHandlers():
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler = logging.StreamHandler()
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
            openai_api_key = os.getenv("OPENAI_API_KEY_OAI")
            self.client = AsyncOpenAI(api_key=openai_api_key)
            self.model = model
            self.semaphore = asyncio.Semaphore(10)
            self.logger.info("GPT initialized")

        async def analyze(self, input_df: pl.DataFrame) -> pl.DataFrame:
            async def process_single_group(group_key, group_df) -> dict:
                try:
                    # Extract the grouping columns
                    # Use these to annotate the return dictionary
                    host_name, group_leader_pid = group_key

                    user_context = f"""<user>
        <name>{group_df["user.name"].unique()[0]}</name>
        <department>{group_df["user.department"].unique()[0]}</department>
        <title>{group_df["user.title"].unique()[0]}</title>
        <city>{group_df["user.geo.city_name"].unique()[0]}</city>
        <state>{group_df["user.geo.region_name"].unique()[0]}</state>
    </user>
                    """
                    user_context_solution = "ZiIiIjx1c2VyPgogICAgPG5hbWU+e2dyb3VwX2RmWyJ1c2VyLm5hbWUiXS51bmlxdWUoKVswXX08L25hbWU+CiAgICA8ZGVwYXJ0bWVudD57Z3JvdXBfZGZbInVzZXIuZGVwYXJ0bWVudCJdLnVuaXF1ZSgpWzBdfTwvZGVwYXJ0bWVudD4KICAgIDx0aXRsZT57Z3JvdXBfZGZbInVzZXIudGl0bGUiXS51bmlxdWUoKVswXX08L3RpdGxlPgogICAgPGNpdHk+e2dyb3VwX2RmWyJ1c2VyLmdlby5jaXR5X25hbWUiXS51bmlxdWUoKVswXX08L2NpdHk+CiAgICA8c3RhdGU+e2dyb3VwX2RmWyJ1c2VyLmdlby5yZWdpb25fbmFtZSJdLnVuaXF1ZSgpWzBdfTwvc3RhdGU+CjwvdXNlcj4KICAgICAgICAgICAgICAgICIiIg=="

                    host_context = f"""<host>
        <macos_version>{group_df["host.os.family"][0]}</macos_version>
        <name>{host_name}</name>
    </host>
                    """
                    host_context_solution = "ZiIiIjxob3N0PgogICAgPG1hY29zX3ZlcnNpb24+e2dyb3VwX2RmWyJob3N0Lm9zLmZhbWlseSJdWzBdfTwvbWFjb3NfdmVyc2lvbj4KICAgIDxuYW1lPntob3N0X25hbWV9PC9uYW1lPgo8L2hvc3Q+CiAgICAgICAgICAgICAgICAiIiI="

                    process_data = group_df.sort("@timestamp", "process.pid").select(
                        "@timestamp", "process.pid", "process.parent.pid", "process.parent.name", "process.command_line", "process.working_directory"
                    ).to_pandas().to_markdown()
                    process_data_solution = "Z3JvdXBfZGYuc29ydCgiQHRpbWVzdGFtcCIsICJwcm9jZXNzLnBpZCIpLnNlbGVjdCgKICAgICAgICAgICAgICAgICAgICAiQHRpbWVzdGFtcCIsICJwcm9jZXNzLnBpZCIsICJwcm9jZXNzLnBhcmVudC5waWQiLCAicHJvY2Vzcy5wYXJlbnQubmFtZSIsICJwcm9jZXNzLmNvbW1hbmRfbGluZSIsICJwcm9jZXNzLndvcmtpbmdfZGlyZWN0b3J5IgogICAgICAgICAgICAgICAgKS50b19wYW5kYXMoKS50b19tYXJrZG93bigp"

                    system_message = system_prompt + user_context + host_context

                    user_message = f"""
    Beginning of commands for analysis:
    Processes: {process_data}
    """

                    # Get GPT analysis
                    analysis =  await self.make_completion(system_message, user_message)

                    # Create the return dictionary
                    result = {
                        "host.name": host_name,
                        "process.group_leader.pid": group_leader_pid, 
                        "analysis": analysis.analysis,
                        "risk_score": analysis.risk_score,
                        "ttps": analysis.ttps
                    }
                    return result
                except Exception as e:
                    self.logger.error(f"Error processing group {group_key}: {e}")
                    return {
                        "host.name": host_name,
                        "process.group_leader.pid": group_leader_pid,
                        "error": str(e),
                    }

            # Create the groups, then kick off an async request for each group
            grouped = input_df.group_by(["host.name", "process.group_leader.pid"])
            tasks = [
                process_single_group(group_key, group_df)
                for group_key, group_df in grouped
            ]
            results = []
            for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                result = await coro
                results.append(result)
            return pl.DataFrame(results)

        @backoff.on_exception(backoff.expo, openai.RateLimitError, max_time=60, max_tries=6)
        async def make_completion(self, system_message: str, user_message: str) -> RiskEvent:
            async with self.semaphore:
                completion = await self.client.responses.parse(
                    model = self.model,
                    instructions = system_message,
                    input = user_message,
                    text_format = RiskEvent
                )
                return completion.output_parsed

        """
        If you want, swap this function into `await self.make_completion` above to see what the messages are
        """
        async def print_messages(self, system_message, user_message):
            print("--------------")
            print(system_message)
            print(user_message)

    return (GPT,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now create an instance of your GPT class, setting the model to `gpt-5-mini`. We'll use the mini model for testing since it is considerably cheaper than the full model.
    """)
    return


@app.cell
def _(GPT):
    gpt = GPT()
    return (gpt,)


@app.cell
def _(mo):
    mo.md(r"""
    Now we can analyze the processes by calling `gpt.analyze()`, passing in `merged_df` as the input.

    Let's preview what the analysis results look like before doing the full dataframe of commands. We can use `.sample()` to only send a subset of the dataframe.
    """)
    return


@app.cell
async def _(gpt, merged_df):
    analysis_df = await gpt.analyze(merged_df.sample(25))
    return (analysis_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And here's what the results look like.
    """)
    return


@app.cell
def _(analysis_df):
    analysis_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How do these results look? One thing that should stand out is that the analysis is a couple of paragraphs, which makes it fairly difficult to quickly triage which processes need another layer of review.

    To make this easier, we can turn to [structured outputs](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses). Structured outputs force the model to conform to a schema that you provide. Let's create a schema for the following fields in our output:

    - `risk_score`: a number 1-10 for how risky the processes are
    - `ttps`: a list of MITRE ATT&CK strings
    - `analysis`: a string for the model to output what the processes were doing

    Create the schema class below, then:

    1. Go back to where you created your GPT class above
    2. Update the `make_completions` function:
        -  change the call to `client.responses.parse` instead of `client.responses.create`.
        -  add the `text_format` parameter to the `client.responses.parse` call. Set it to `RiskEvent`.
        -  change the return from the plain text response to `return completion.output_parsed`
    3. Update `process_single_group`
        -  Update the `result` dict. Previously, the unstructured call returned plain text.
        -  Now, `analysis` is a `RiskEvent` object, so we want to retrieve `analysis`,`risk_score`, and `ttps` keys
    """)
    return


@app.cell
def _():
    from pydantic import BaseModel 

    class RiskEvent(BaseModel):
        _solution = "cmlza19zY29yZTogaW50IAp0dHBzOiBsaXN0W3N0cl0KYW5hbHlzaXM6IHN0cg=="
        risk_score: int 
        ttps: list[str]
        analysis: str

    return (RiskEvent,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a new instance of your GPT class and a new structured_analysis_df and sample the results.
    """)
    return


@app.cell
async def _(GPT, merged_df):
    structured_gpt = GPT()
    structured_analysis_df = await structured_gpt.analyze(merged_df.sample(25))
    structured_analysis_df
    return (structured_gpt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Your dataframe should show `host.name`, `process.group_leader.pid`, `risk_score`, `ttps`, and `analysis`. With these columns, we can filter and sort on `risk_score` and use that to set thresholds where we might create an alert. For example, if `risk_score` is above 8, that might be our cue that the processes deserve human attention.

    As an alert triager, we can then read the `analysis` column to see why the alert was created and decide to take further action. We can use the `ttps` column as additional information for what may have been attempted.

    If you dataframe contains all the columns, we can process the full `merged_df`.
    """)
    return


@app.cell
async def _(merged_df, structured_gpt):
    full_results = await structured_gpt.analyze(merged_df)
    return (full_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Evaluation
    Let's evaluate how GPT worked as a detector.

    First we will mark certain processes as malicious or not based on ground truth data. The following cell provides you the list of PGIDs that were tied to malicious activity.

    We will then create a new column `malicious` and set it to 1 when the `host.name` and `process.group_leader.pid` values match, and set to 0 when not.

    Lastly we'll create a new dataframe called `final_df` that holds all the information we want: processes, users, malicious ground truth, and GPT detections.
    """)
    return


@app.cell
def _(full_results, merged_df, pl):
    conditions = [
        (merged_df['host.name'] == 'scr-office-imac.local') & (merged_df['process.group_leader.pid'].is_in([10957, 11169, 11176, 11181, 11295, 11298, 12826, 12828, 12829,11138])),
        (merged_df['host.name'] == 'scr-it-mac.local') & (merged_df['process.group_leader.pid'].is_in([11901, 11902, 12206,12220, 12238, 12353, 12520, 12532, 12658, 12949, 14703, 14703, 14705,12951]))
    ]

    _annotated_df = merged_df.with_columns(
        pl.when(conditions[0] | conditions[1])
          .then(1)
          .otherwise(0)
          .alias("malicious")
    )

    final_df = _annotated_df.join(full_results, on=["host.name", "process.group_leader.pid"])
    return (final_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here you can inspect items based whether the PGID was marked as malicious and GPT marked it with high risk.
    """)
    return


@app.cell
def _(final_df, pl):
    final_df.filter(
        (pl.col("malicious") == 1)
    ).group_by(["host.name", "process.group_leader.pid"]).agg([
        pl.max("malicious").alias("malicious"),
        pl.max("risk_score").alias("risk_score"),
        "process.command_line",
        pl.first("analysis")
    ]).filter(
        (pl.col("malicious") == 1) & (pl.col("risk_score") > 1) # Change risk_score to see how large each result set is.
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's plot a confusion matrix. This matrix will be a bit different than previous ones we've used - it will plot the TP, FP, TN, and FN by the risk score threshold, which can help you see where a useful threshold might be.
    """)
    return


@app.cell
def _(final_df, pl):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np 

    thresholds = list(range(1, 11))  # Risk score thresholds from 1 to 10

    # Initialize matrix: rows=TP,FP,TN,FN; cols=thresholds
    conf_matrix = np.zeros((4, len(thresholds)), dtype=int)

    for idx, _threshold in enumerate(thresholds):
        _pred_col = (pl.col("risk_score") >= _threshold).cast(pl.Int8)
        _df_pred = final_df.with_columns(_pred_col.alias("pred_malicious"))
        _agg_df = _df_pred.group_by(["host.name", "process.group_leader.pid"]).agg([
            pl.max("malicious").alias("malicious"),
            pl.max("pred_malicious").alias("pred_malicious")
        ])
        _tp = ((_agg_df["malicious"] == 1) & (_agg_df["pred_malicious"] == 1)).sum()
        _fp = ((_agg_df["malicious"] == 0) & (_agg_df["pred_malicious"] == 1)).sum()
        _tn = ((_agg_df["malicious"] == 0) & (_agg_df["pred_malicious"] == 0)).sum()
        _fn = ((_agg_df["malicious"] == 1) & (_agg_df["pred_malicious"] == 0)).sum()
        conf_matrix[:, idx] = [_tp, _fp, _tn, _fn]

    labels = ["TP", "FP", "TN", "FN"]

    plt.figure(figsize=(12, 3))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues",
                xticklabels=thresholds, yticklabels=labels)
    plt.xlabel("Risk Score Threshold")
    plt.ylabel("Confusion Matrix Cell")
    plt.title("Confusion Matrix vs. Risk Score Threshold")
    plt.tight_layout()
    plt.show()
    return plt, thresholds


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can also plot this as a line graph.
    """)
    return


@app.cell
def _(final_df, pl, plt, thresholds):
    tpr_list = []
    fpr_list = []
    precision_list = []
    recall_list = []

    for threshold in thresholds:
        pred_col = (pl.col("risk_score") >= threshold).cast(pl.Int8)
        df_pred = final_df.with_columns(pred_col.alias("pred_malicious"))
        agg_df = df_pred.group_by(["host.name", "process.group_leader.pid"]).agg([
            pl.max("malicious").alias("malicious"),
            pl.max("pred_malicious").alias("pred_malicious")
        ])
        tp = ((agg_df["malicious"] == 1) & (agg_df["pred_malicious"] == 1)).sum()
        fp = ((agg_df["malicious"] == 0) & (agg_df["pred_malicious"] == 1)).sum()
        tn = ((agg_df["malicious"] == 0) & (agg_df["pred_malicious"] == 0)).sum()
        fn = ((agg_df["malicious"] == 1) & (agg_df["pred_malicious"] == 0)).sum()

        # True Positive Rate and False Positive Rate
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tpr_list.append(tpr)
        fpr_list.append(fpr)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision_list.append(precision)
        recall_list.append(recall)

    # Add (0,0) and (1,1) for a proper ROC curve
    fpr_plot = [0] + fpr_list + [1]
    tpr_plot = [0] + tpr_list + [1]

    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, tpr_list, marker='o', label='TPR (Recall)')
    plt.plot(thresholds, fpr_list, marker='o', label='FPR')
    plt.plot(thresholds, precision_list, marker='o', label='Precision')
    plt.xlabel("Risk Score Threshold")
    plt.ylabel("Rate")
    plt.title("Rates vs Threshold")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reflection
    Which threshold seems to be the best? Even at that threshold, how do the number of false positives vs true positives compare? Would you want to triage these alerts?

    Try changing the system/developer prompt and see how that changes the efficacy of GPT as a detector. What additional context could you add, or what should you take away that may be influencing the model negatively?

    You can use the following to re-evaluate only the known bad commands with `new_results_df = await structured_gpt.analyze(known_bad)`

    You can also try switching to the larger `gpt-5` model and see how the analysis differs from the mini model. Do the `risk_score`, `ttps`, or `analysis` values differ? Also think about the knowledge cut-off dates for these models and how that might impact the accuracy of the MITRE ATT&CK values. How could we improve the MITRE classifications?
    """)
    return


@app.cell
def _(merged_df, pl):
    known_bad = merged_df.filter(
        (
            (pl.col("host.name") == "scr-office-imac.local") &
            (pl.col("process.group_leader.pid").is_in([10957, 11169, 11176, 11181, 11295, 11298, 12826, 12828, 12829, 11138]))
        )
        |
        (
            (pl.col("host.name") == "scr-it-mac.local") &
            (pl.col("process.group_leader.pid").is_in([11901, 11902, 12206, 12220, 12238, 12353, 12520, 12532, 12658, 12949, 14703, 14705, 12951]))
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, let's save the `final_df` to use in the next module.
    """)
    return


@app.cell
def _(final_df):
    final_df.write_parquet("data/gpt_detector_results.parquet")
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
