# Purpose
This repository contains cyber threat hunting investigations.

## File layout
- context/ contains markdown files that provide general information about the organization, its network, and security telemetry. ALWAYS reference files here.
- intel/ contains markdown, PDF, and other file types that provide specific information about cyber threats. Reference these files when asked to.
- skills/ contain pre-build skills for distribution.
- utils/ contain utility scripts that may assist with threat hunting.

# Conducting threat hunts
Threat hunts consist of three stages: prepare, execute, act.

## Prepare
You will get a threat hunting topic from a user. Perform the following:
1. Research the topic from any intel they mention, use any research skills, and search the Internet. When searching, focus on intelligence reporting about the threat topic.
2. Generate hypotheses. A hunt hypothesis is testable - it can be proven or disproven. For example, "a threat actor may be exfiltrating sensitive data using DNS tunneling".
3. Refine the hypothesis using knowledge from `context/` or from the user's query to make the hypothesis more specific.
4. Create a hunt plan. This plan should define the overall goal of the hunt and list each hypothesis and what data is needed to prove it.

## Execute
This stage gathers and analyzes data from the SIEM. You will perform the following steps in iteration to chase down each hypothesis and to gather enough evidence points to prove them.
1. Gather data by querying the SIEM.
2. Process the data. You should keep a local "cache" of the data by writing SIEM outputs to temporary files you can reference.
3. Analyze the data to prove or disprove the hypotheses. Keep in mind that there is rarely a single piece of evidence that proves a hypothesis.

## Act
This stage acts on the findings.
1. Document findings. For each hypothesis you must document whether it was proven or disproven and link to the evidence as to why.
2. Report the findings. Write a professional, concise report grounded in MITRE ATT&CK.

### Creating hypotheses
You can create hypotheses from multiple viewpoints. Where possible, combine multiple viewpoints to create stronger hypotheses.
- Intelligence based: focused on a specific threat and how they operate.
    - Ex: APT28 will use WinRAR to archive collected data with password protection
- Situational awareness based: focused on a temporal threat.
    - Ex: Increased malvertising makes it likely one of our developers downloads malware masquerading as Cursor.
- Domain expertise based: uses knowledge of the operational environment.
    - Ex: Based on our network configuration an attacker must steal SSH keys to move laterally.

### Pivoting
Since a single piece of evidence is unlikely to prove a hypothesis you must pivot between data sources.
- Pivot from network data to host data by linking identifiers. For example, to find a reverse shell you might link an IP address captured in network data to a specific host, then from the host to the process responsible for the connection.
- Pivot on process execution chains. Always look to see what the parent process chain is to help identify initial access points. Always look at the children processes to find what actions were taken. For example, a Cobalt Strike Beacon parent process may show it was started via a webshell and looking at the children processes may show reconnaissance, lateral movement, or collection.
- Pivot on file operations by processes. Look for files created, modified, or deleted. This may show persistence, timestomping, or defense evasion.
- Pivot from host data to network data to identify command and control or exfiltration.

### Analysis
The following frameworks should be used when analyzing data to prove hypotheses.
- Pyramid of pain: helps to understand the relative value of indicator types. Higher value indicators give greater evidence.
- Diamond model: understand relationships between detection points and adversary operations.
- Cyber kill chain: understand that adversary activity does not happen in isolation. Look for activity earlier and later in the kill chain to understand the scope and impact.

### Enrichment
Use enrichment skills to gain further insight into indicators found and to help with clustering and attribution.