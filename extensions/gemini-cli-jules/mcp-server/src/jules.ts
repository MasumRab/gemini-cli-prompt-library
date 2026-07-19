#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 *
 * Jules MCP Server for Gemini CLI
 *
 * Uses @google/jules-sdk for session management instead of shelling out
 * to the `jules` CLI binary. This provides:
 *   - Native TypeScript API (no subprocess overhead)
 *   - Real-time streaming via session.stream()
 *   - Synchronous ask() for request/response patterns
 *   - waitFor() for state-based flow control
 *   - Automatic retry with exponential backoff (built into SDK)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { jules, type SessionState } from '@google/jules-sdk';

const server = new McpServer({
  name: 'jules-mcp-server',
  version: '0.2.0',
});

// --- Tool: start_new_jules_task ---

server.tool(
  'start_new_jules_task',
  'Starts a new Jules task in automated mode (fire-and-forget).',
  {
    repo_name: z.string().describe('The GitHub repository in owner/repo format.'),
    user_task_description: z.string().describe('The description of the user task.'),
    base_branch: z.string().default('main').describe('The base branch to start from.'),
  },
  async (input: {
    repo_name: string;
    user_task_description: string;
    base_branch: string;
  }): Promise<CallToolResult> => {
    try {
      const run = await jules.run({
        prompt: input.user_task_description,
        source: { github: input.repo_name, baseBranch: input.base_branch },
      });
      const info = await run.session.info();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ sessionId: info.id, state: info.state }),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Tool: send_message ---

server.tool(
  'send_message',
  'Sends a message to an existing Jules session (fire-and-forget).',
  {
    session_id: z.string().describe('The Jules session ID.'),
    message: z.string().describe('The message to send.'),
  },
  async (input: { session_id: string; message: string }): Promise<CallToolResult> => {
    try {
      const session = jules.session(input.session_id);
      await session.send(input.message);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ status: 'sent', sessionId: input.session_id }),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Tool: ask_jules ---

server.tool(
  'ask_jules',
  'Sends a message and waits for the agent reply (synchronous request/response).',
  {
    session_id: z.string().describe('The Jules session ID.'),
    question: z.string().describe('The question to ask.'),
  },
  async (input: { session_id: string; question: string }): Promise<CallToolResult> => {
    try {
      const session = jules.session(input.session_id);
      const reply = await session.ask(input.question);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(reply),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Tool: approve_plan ---

server.tool(
  'approve_plan',
  'Approves the pending plan for a Jules session.',
  {
    session_id: z.string().describe('The Jules session ID.'),
  },
  async (input: { session_id: string }): Promise<CallToolResult> => {
    try {
      const session = jules.session(input.session_id);
      await session.approve();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ status: 'approved', sessionId: input.session_id }),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Tool: get_session_info ---

server.tool(
  'get_session_info',
  'Retrieves the current state and info of a Jules session.',
  {
    session_id: z.string().describe('The Jules session ID.'),
  },
  async (input: { session_id: string }): Promise<CallToolResult> => {
    try {
      const session = jules.session(input.session_id);
      const info = await session.info();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(info),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Tool: wait_for_state ---

server.tool(
  'wait_for_state',
  'Waits until a Jules session reaches a specific state (or terminal state).',
  {
    session_id: z.string().describe('The Jules session ID.'),
    target_state: z.string().describe('Target state: awaitingPlanApproval, inProgress, completed, etc.'),
    timeout_ms: z.number().optional().default(300000).describe('Max wait time in ms (default: 300000 = 5 min).'),
  },
  async (input: {
    session_id: string;
    target_state: string;
    timeout_ms: number;
  }): Promise<CallToolResult> => {
    try {
      const session = jules.session(input.session_id);
      await session.waitFor(input.target_state as SessionState, {
        timeoutMs: input.timeout_ms,
      });
      const info = await session.info();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(info),
        }],
      };
    } catch (err) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: err instanceof Error ? err.message : String(err) }),
        }],
      };
    }
  }
);

// --- Server startup ---

async function startServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

if (process.env.NODE_ENV !== 'test') {
  startServer();
}

export default server;
export { startNewJulesTask } from './jules.js';
