# Transitioning Jules Session Monitoring from Polling to Streaming

## Executive Summary
Replacing polling with streaming in Jules session monitoring requires identifying existing polling mechanisms across shell scripts, Python files, and documentation, then adopting the Jules SDK's asynchronous iterator-based streaming methods while preserving compatibility with current skills and runbooks. The SDK provides history(), updates(), and stream() methods returning AsyncIterators of Activity objects, enabling real-time monitoring with reduced latency and request overhead. Migration involves replacing polling loops with async iteration patterns, maintaining existing configuration options, and ensuring all integrated components continue functioning without modification.

## Current Polling Mechanisms in Jules Session Monitoring

Polling mechanisms exist across multiple file types in the Jules session monitoring codebase. Shell scripts exhibit classic polling patterns: retrieve_sessions.sh contains a loop over session IDs with individual API calls followed by sleep 1 intervals, and jules_sync_all.sh iterates over local session JSON files to refresh metadata via repeated API calls [1]. Python files show polling in the paginate_all function of cass_search.py, which repeatedly calls the search API to fetch paginated results [2]. Documentation references polling configuration in the Jules SDK README, demonstrating how to set pollingIntervalMs and timeout via jules.with() [3]. Source code analysis confirms the SDK implements polling through NetworkAdapter.rawStream() with a default 5000ms interval and hybrid pagination/polling strategies in streaming.ts [4][5]. The monitoring tool jules_monitor.py uses time.sleep(MONITOR_INTERVAL) with a 60-second interval for polling [9].

## Jules SDK Streaming Capabilities

The Jules SDK provides streaming via Session methods returning AsyncIterators of Activity objects: history() delivers a cold stream of past activities from local storage then network, updates() provides a hot stream of only future activities from the network, and stream() offers a hybrid approach yielding history followed by live updates [3][4][5][6][7][8][9][10]. Activity objects include types such as planGenerated, agentMessaged, progressUpdated, and sessionCompleted, containing artifacts like code changes, bash output, and media [3][4]. The streaming implementation handles pagination, automatic polling when no more pages exist, deduplication using high-water marks, and error handling with initial 404 retries using exponential backoff [5][6][7][8][9][10]. No prior investigation documents recommend specific streaming technologies like WebSockets, Server-Sent Events, or gRPC; the current approach relies on HTTP polling mechanisms [8].

## Existing Skills, Runbooks, and Integrations to Preserve

Existing components requiring preservation include two skills: jules-api and jules-session-manager [5]. Integration points referenced in these skills are scripts/jules_tools/session_pr_triage.py and agents/openai.yaml [5]. Additional monitoring-specific tools requiring updates but not replacement are jules_monitor.py, the API client (jules_api_client.py), and the STREAMING_RESEARCH.md planning document [9]. The standardized tools/skills structure must remain unchanged, with no additional .sh, .py, .md files or skills identified beyond this structure [9]. Note that specified runbook files (.agents/commands/jules-manager.py and .kilo/commands/jules-manager.py) were not found in the workspace [7].

## Latency and Reliability Requirements

Current polling latency ranges from 0 to the polling interval, with a default interval of 5000ms (5 seconds) for activity checks [4][6]. Initial session activity polling includes retry logic for 404 errors: up to 10 retries with 1000ms initial delay and exponential backoff, capped at 30000ms [4][6]. Third-party monitoring indicates Jules maintains high historical uptime (100% except Nov-2025 at 99.86%) with monthly average response times between 142ms and 211ms [6]. Internal benchmarks show median "Cosine Proximity Latency" of 0.0024ms for context processing [6]. Streaming implementations reduce worst-case latency by a factor of the polling interval (e.g., 5x-30x) and average latency from roughly half the interval to under one second, while decreasing request overhead from N/clients ÷ interval to negligible persistent connection maintenance [11][12].

## Implementation Plan for Streaming Injection

Replace polling mechanisms with SDK streaming methods through the following steps:

1. **Shell script updates**: Transform loops in retrieve_sessions.sh and jules_sync_all.sh to use session.stream() AsyncIterators instead of individual API calls with sleep intervals [1]. Replace polling patterns with async iteration handling activity types and artifacts.

2. **Python file modifications**: Replace the paginate_all function in cass_search.py and similar polling patterns with AsyncIterator consumption from session.stream() or session.updates() [2]. Implement for-await loops to process activities as they arrive.

3. **SDK configuration**: Maintain existing pollingIntervalMs and timeout configuration options through jules.with() for backward compatibility, as streaming methods incorporate these parameters for underlying update polling [3][4].

4. **Activity processing**: Update consumers to handle Activity objects from AsyncIterators, extracting data from activity.type and activity.artifacts rather than parsing session metadata responses [3][4].

5. **Error handling**: Implement try/catch blocks around AsyncIterator consumption to manage stream errors, preserving existing error handling patterns from polling helpers [2].

6. **Validation**: Ensure all skills (jules-api, jules-session-manager), integration points (scripts/jules_tools/session_pr_triage.py, agents/openai.yaml), and monitoring tools (jules_monitor.py, API client) operate correctly with streaming outputs [5][9].

This approach preserves all existing functionality while injecting real-time streaming capabilities, eliminating polling latency gaps and reducing request overhead through persistent connections that deliver activities as they occur.
