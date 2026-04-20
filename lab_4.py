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
    # 0xe: Long-running coding agents
    In this notebook we focus on long-running coding agents such as Codex and Claude Code. These systems do more than answer prompts. They inspect repositories, use tools, run commands, revise plans, and keep working until a task is done.

    **Agenda**

    - Agent harnesses
    - Codex and Claude Code
    - Skills
    - ExecPlans
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What makes an agent long-running?
    A normal assistant call is one request and one response. A long-running agent can work through many internal steps before it stops.

    In practice, that means it can:

    - inspect many files
    - call tools repeatedly
    - keep notes and update a plan
    - verify its own work
    - continue until it has a usable result

    That is what tools like Codex and Claude Code are designed to do.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Agent harnesses
    The most important idea here is the **agent harness**.

    The model is only one part of the system. The harness is the runtime around the model that:

    - builds the model context
    - exposes tools
    - enforces permissions and safety rules
    - manages plan updates and progress
    - decides how file edits and command output flow back into the loop

    This is why long-running coding agents feel different from a plain API call. The harness is doing a lot of the real engineering work around the model.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why harnesses matter
    In software and security workflows, reliability usually depends less on clever prompting and more on the surrounding harness.

    A good harness gives the agent:

    - a controlled workspace
    - a known toolset
    - persistent instructions
    - a way to inspect and verify state
    - boundaries for what it can and cannot do

    OpenAI documents this explicitly for Codex in [Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/) and [Unlocking the Codex harness](https://openai.com/index/unlocking-the-codex-harness/).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Codex
    Codex is a coding agent from OpenAI built around a shared harness. It can work in the terminal, in the Codex app, and in cloud-backed task execution.

    The key parts for long tasks are:

    - repository-aware execution
    - file reads and edits
    - shell command execution
    - durable repo instructions through `AGENTS.md`
    - reusable skills
    - support for parallel and background work in the app

    See [Codex](https://openai.com/codex/), [Introducing Codex](https://openai.com/index/introducing-codex/), and [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-codex-in-chatgpt).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Command-line access
    Command-line access is a major reason these systems are useful. It lets the agent interact with the real environment and manage context.

    Examples:

    - `rg` to search a repo quickly
    - `git diff` and `git status` to inspect changes
    - `pytest` or `uv run` to verify code
    - `plutil -p` to inspect macOS property lists
    - `log show` to query macOS unified logs
    - `sqlite3` and `jq` to inspect local artifacts

    In macOS security work, that means the agent can do things like:

    ```bash
    plutil -p ~/Library/LaunchAgents/com.suspicious.agent.plist
    log show --predicate 'process == "launchd"' --last 1h
    sqlite3 triage.db 'select * from processes limit 10;'
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Durable instructions
    Long-running agents need instructions that survive across many tool calls.

    Common examples:

    - Codex uses `AGENTS.md`
    - Claude Code uses `CLAUDE.md`

    These files often define:

    - mission
    - preferred tools
    - style rules
    - validation steps
    - reporting format
    - escalation rules
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### AGENTS.md
    ```
    ## Mission
    Investigate suspicious macOS activity and produce evidence-backed findings.

    ## Operating rules
    - Prefer terminal-native tools such as `rg`, `plutil`, `sqlite3`, `jq`, `log show`, and `codesign -dv`
    - Do not invent artifacts that are not present in the evidence
    - Save short notes as you go so you can build a final report
    - Call out uncertainty explicitly

    ## Investigation priorities
    1. Identify the initial execution chain
    2. Look for persistence
    3. Look for outbound network activity
    4. Summarize likely impact and recommended containment

    ## ExecPlans
    When a task will likely span many files or take longer than a normal turn, create or update an ExecPlan before making major edits.
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Skills
    Skills are reusable instruction bundles. They are not the same thing as tools.

    - A **tool** gives the agent a capability
    - A **skill** tells the agent how to apply capabilities to a recurring task

    This matters in long-running work because the same task shapes repeat.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Skill anatomy

    ```text
    .
    ├── SKILL.md
    ├── scripts/
    ├──── myscript.py
    ├── examples/
    └── templates/
    ```

    Good security skills might cover:

    - log triage
    - IOC enrichment
    - report writing
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Skill structure
    Skills consist of:

    YAML Frontmatter
    - Describes **when** to use the skill
    - Loaded by the agent at startup. As it is smaller, it saves context window.

    Skill text
    - THe prompt/instruction on **how** to use the skill
    - Loaded when the skill is used.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Why skills matter
    Skills improve consistency across long tasks.

    Instead of re-prompting the agent every time with detailed instructions for how to inspect persistence or summarize evidence, you package that logic once and reuse it.

    Both Codex and Claude Code support skills as part of the harness. In a custom SDK-based agent, you would usually recreate this idea with prompts, helper functions, or internal workflow code.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ExecPlans
    For multi-hour work, a short prompt is usually not enough. You need a plan artifact the agent can follow and update.

    OpenAI documents one good pattern for this with `PLANS.md`, where the repo teaches Codex that complex work should begin with an **ExecPlan**.

    ExecPlans are part of the harness, not the model.

    See [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What an ExecPlan should contain

    - problem statement
    - constraints and non-goals
    - relevant files and systems
    - implementation plan
    - verification commands
    - risks and rollback thinking
    - clear definition of done

    Ask the model to make one
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Minimal ExecPlan skeleton

    ```md
    # ExecPlan: Investigate suspicious LaunchAgent chain

    ## Goal
    Determine whether the LaunchAgent establishes persistence and outbound C2.

    ## Constraints
    Do not modify artifacts. Collect evidence first.

    ## Files and data
    - `~/Library/LaunchAgents/`
    - unified logs
    - endpoint telemetry database

    ## Plan
    1. Inspect plist contents and referenced binaries
    2. Build a timeline from logs and telemetry
    3. Check network indicators and code-signing state
    4. Produce a concise incident summary

    ## Verification
    List the exact commands used to support each conclusion
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Long-running coding agents vs the OpenAI Agents SDK

    |Question|Codex / Claude Code|OpenAI Agents SDK|
    |---|---|---|
    |Who owns orchestration?|The product runtime|You do|
    |Who defines shell access and edit flow?|The harness|You do|
    |Who manages repo instruction files?|The harness|You do if you want that feature|
    |Who handles approval UX and policy?|The harness|You do|
    |Who decides planning conventions?|Mostly the harness plus repo docs|You do|
    |Best use case|Do work in an existing repo|Build a custom agent system|
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Lab 0xe
    In this lab we'll be using Codex to perform threat hunts.

    ## AGENTS.md
    The repo provides a baseline AGENTS.md file. Take a minute to inspect it.

    The AGENTS.md file provides guidance on:
    - The repository layout.
    - How to conduct a threat hunt.

    Inspect the directories referenced by the AGENTS.md file, especially the `context` directory. This folder contains a few markdown files that describe what telemetry is available in our SIEM and provides some starter queries so Codex knows how to use the data that's available.

    The hunting guidance should cause Codex to first prepare for a hunt by taking your prompt and performing research on it. Codex can natively search the web and read local files. Then it will generate some hypotheses, and the AGENTS.md file provides some example hypotheses to show Codex what they should look like. The file then provides guidance on retrieving data from the SIEM and analyzing the results to compare against the hypotheses it makes.

    It does _not_ provide guidance on how to structure a threat hunting report. You may want to add a section that describes what you want your report to look like.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Start a hunt

    There are two main scenarios. Both of these contain an entire adversary killchain from initial access to actions on objective.

    Here is some general information about the organization you are defending:

    > Dunder Mifflin is a regional supplier of various paper products, including copy paper, stationery, and other office supplies. The company's geographical footprint primarily centers around its Mid-Atlantic and New England offices. Due to the COVID pandemic, there has been an increase in remote work and remote access (such as RDP and VPN technologies) were hastily implemented to keep the business afloat.

    > The challenges faced by the company's business climate revolve around the increasing digitization and the shift towards paperless offices in the modern world. As technology advances, the demand for traditional paper products declines, posing a significant threat to the company's long-term sustainability. Additionally, it faces fierce competition from other paper suppliers and online retailers, requiring the sales team to work hard to secure and retain customers, which can lead to them taking shortcuts to keep customers happy. The tough margins leave little room for updating computers and maintaining software licenses. The office culture itself also presents challenges, with various quirky and sometimes counterproductive personalities creating a unique and often chaotic work environment.

    ### Scenario 1

    > The company is currently in high spirits due to the recent successful acquisition of a significant contract with the South Korean Ministry of National Defense. This represents a huge lifeline and ensures everyone keeps their jobs.

    **When**: 2024-07-29 to 2024-08-02

    Intel: use `intel/scenario1/intel.pdf`.

    ### Scenario 2

    > Due to its prior breaches, Dunder Mifflin has retained JHConsulting to help them identify and remediate security issues. Working with JHConsulting, Dunder Miffilin admins have been able to patch the pfSense vulnerability, but the remaining vulnerabilities were deprioritized until after the holidays. JHConsulting also pulled relevant OSINT from dark web access forums.

    **When**: 2024-11-22 to 2024-11-27

    Intel: use `intel/scenario2/intel1.pdf` and `intel/scenario2/intel2.pdf`.

    To start a hunt, provide Codex with:
    - Your overall intent
    - The timeframe to scope the hunt
    - The intel references by typing `@intel` and selecting the appropriate files.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Hunt progress
    Watch Codex work. How long does it work for before producing an output?

    Some things to look for:
    - Does it draft a plan? If not, try using `/plan` to turn plan mode on.
    - Does it stop after finding one evidence of attack? If so, ask it follow up questions like "Did the attacker access other computers?"
    - Does it write an intermediate report? If not, ask it to draft it's output as it goes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Create a skill
    After Codex has finished its investigation you should still have some lingering questions, mainly around attribution. We can use threat intelligence services like VirusTotal to help close this gap.

    You do not currently have a skill for this, but you can ask Codex to make one with a prompt like:

    ```
    $skill-creator make a skill that uses the virustotal api
    to enrich ip addresses, domain names, and file hashes.
    use the api key provided in our .env file
    ```

    Once Codex makes the skill, ask it to use it to enrich the IOCs it found in its investigation and to update its report.

    Review the report and see how it did.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reflection
    Which parts of the harness mattered most for the quality of the result?

    Where did the agent still need human judgment?

    If you were operationalizing this for defenders, what skills, hooks, or planning rules would you add next?
    """)
    return


if __name__ == "__main__":
    app.run()
