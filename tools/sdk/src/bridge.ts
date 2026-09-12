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

import { jules, type SessionState, type Activity } from "@google/jules-sdk";

const USAGE = `Usage: bridge.js <command> [args]

Commands:
  stream <sessionId>              Stream activities in real-time (Ctrl+C to stop)
  ask <sessionId> <prompt>        Send message and wait for agent reply
  waitFor <sessionId> <state>     Wait until session reaches state
  run <repo> <branch> <prompt>    Start automated task (fire-and-forget)
  result <sessionId>              Wait for session completion, print outcome
  info <sessionId>                Print session info as JSON
  approve <sessionId>             Approve pending plan
  history <sessionId>              Print all past activities as JSON lines
`;

async function main() {
  const [cmd, ...args] = process.argv.slice(2);

  if (!cmd) {
    console.error(USAGE);
    process.exit(1);
  }

  try {
    switch (cmd) {
      case "stream":
        await streamActivities(args[0]);
        break;
      case "ask":
        await askSession(args[0], args.slice(1).join(" "));
        break;
      case "waitFor":
        await waitForState(args[0], args[1] as SessionState);
        break;
      case "run":
        await runTask(args[0], args[1], args.slice(2).join(" "));
        break;
      case "result":
        await getResult(args[0]);
        break;
      case "info":
        await getInfo(args[0]);
        break;
      case "approve":
        await approvePlan(args[0]);
        break;
      case "history":
        await getHistory(args[0]);
        break;
      default:
        console.error(`Unknown command: ${cmd}\n`);
        console.error(USAGE);
        process.exit(1);
    }
  } catch (err) {
    console.error(JSON.stringify({ error: err instanceof Error ? err.message : String(err) }));
    process.exit(1);
  }
}

/**
 * Stream activities in real-time. Prints each activity as a JSON line.
 * Keeps running until the session reaches a terminal state or Ctrl+C.
 */
async function streamActivities(sessionId: string) {
  if (!sessionId) {
    console.error("Error: sessionId required");
    process.exit(1);
  }

  const session = jules.session(sessionId);

  // Print history first (flush each line for pipe consumers)
  for await (const activity of session.history()) {
    process.stdout.write(JSON.stringify(activity) + "\n");
  }

  // Then stream updates (flush each line)
  for await (const activity of session.updates()) {
    process.stdout.write(JSON.stringify(activity) + "\n");
  }
}

/**
 * Send a message and wait for the agent's reply.
 * Prints the reply activity as JSON.
 */
async function askSession(sessionId: string, prompt: string) {
  if (!sessionId || !prompt) {
    console.error("Error: sessionId and prompt required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  const reply = await session.ask(prompt);
  console.log(JSON.stringify(reply));
}

/**
 * Wait until the session reaches a specific state.
 * Prints the final session info as JSON.
 */
async function waitForState(sessionId: string, targetState: SessionState) {
  if (!sessionId || !targetState) {
    console.error("Error: sessionId and state required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  await session.waitFor(targetState);
  const info = await session.info();
  console.log(JSON.stringify(info));
}

/**
 * Start an automated (fire-and-forget) task.
 * Prints the session ID immediately, then optionally waits for result.
 */
async function runTask(repo: string, branch: string, prompt: string) {
  if (!repo || !branch || !prompt) {
    console.error("Error: repo, branch, and prompt required");
    process.exit(1);
  }

  const run = await jules.run({
    prompt,
    source: { github: repo, baseBranch: branch },
  });

  // Print session ID immediately so callers can capture it
  console.log(JSON.stringify({ sessionId: run.id }));
}

/**
 * Wait for a session to complete and print the outcome.
 */
async function getResult(sessionId: string) {
  if (!sessionId) {
    console.error("Error: sessionId required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  const outcome = await session.result();
  console.log(JSON.stringify(outcome));
}

/**
 * Print session info as JSON.
 */
async function getInfo(sessionId: string) {
  if (!sessionId) {
    console.error("Error: sessionId required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  const info = await session.info();
  console.log(JSON.stringify(info));
}

/**
 * Approve a pending plan.
 */
async function approvePlan(sessionId: string) {
  if (!sessionId) {
    console.error("Error: sessionId required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  await session.approve();
  console.log(JSON.stringify({ status: "approved", sessionId }));
}

/**
 * Print all past activities as JSON lines.
 */
async function getHistory(sessionId: string) {
  if (!sessionId) {
    console.error("Error: sessionId required");
    process.exit(1);
  }

  const session = jules.session(sessionId);
  for await (const activity of session.history()) {
    console.log(JSON.stringify(activity));
  }
}

main();
