#!/usr/bin/env node
/**
 * Jules SDK Bridge — exposes @google/jules-sdk features to Python tools
 * and shell scripts via a simple CLI interface.
 *
 * The Python tools (tools/api/jules_api_client.py) handle basic CRUD via
 * raw REST. This bridge provides SDK-only features:
 *   - stream:   Real-time activity streaming
 *   - ask:      Send message + await agent reply (synchronous)
 *   - waitFor:  Block until session reaches a specific state
 *   - run:      Fire-and-forget automated task
 *   - result:   Wait for session completion and return outcome
 *
 * Usage from Python:
 *   subprocess.run(["node", "tools/sdk/dist/bridge.js", "stream", SESSION_ID])
 *   subprocess.run(["node", "tools/sdk/dist/bridge.js", "ask", SESSION_ID, "What is the status?"])
 *   subprocess.run(["node", "tools/sdk/dist/bridge.js", "waitFor", SESSION_ID, "awaitingPlanApproval"])
 *
 * Usage from shell:
 *   node tools/sdk/dist/bridge.js stream SESSION_ID
 *   node tools/sdk/dist/bridge.js ask SESSION_ID "What is the status?"
 *   node tools/sdk/dist/bridge.js waitFor SESSION_ID awaitingPlanApproval
 */
export {};
