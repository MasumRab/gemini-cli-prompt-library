---
name: jules-cli
description: Execute Jules CLI commands for creating, monitoring, and managing AI coding sessions. Use when the user asks about Jules CLI, creating Jules sessions, checking Jules status, or working with Google's Jules AI coding agent. Trigger keywords: jules, jules new, jules remote, jules auth.
---

# Jules CLI Commands

Google Jules CLI for asynchronous AI coding agent sessions.

## Installation

```bash
# Via mise
mise install npm-google-jules

# Via npm
npm install -g @google/jules

# Verify
jules --version
```

## Quick Commands

### Create Sessions

```bash
# Launch TUI
jules

# Create session for current repo
jules new "Fix async handler in backend"

# Create session for specific repo
jules new --repo MasumRab/EmailIntelligence "Add API rate limiting"

# Create parallel sessions (3 agents)
jules new --repo owner/repo --parallel 3 "Optimize database queries"

# From TODO list
cat TODO.md | while read task; do jules new "$task"; done
```

### Monitor Sessions

```bash
# List all sessions
jules remote list --session

# List all repos
jules remote list --repo

# Watch session progress
watch -n 5 'jules remote list --session | head -5'
```

### Get Results

```bash
# Pull session result (as patch)
jules remote pull --session SESSION_ID

# Pull and apply to current repo
jules remote pull --session SESSION_ID --apply
```

## EmailIntelligence Examples

```bash
# Backend tasks
jules new --repo MasumRab/EmailIntelligence "Add rate limiting to FastAPI endpoints"
jules new --repo MasumRab/EmailIntelligence --branch scientific "Optimize ML model inference speed"

# Frontend tasks
jules new --repo MasumRab/EmailIntelligence "Refactor React components to use Radix UI primitives"

# Infrastructure
jules new --repo MasumRab/EmailIntelligence "Add Docker compose for production deployment"
jules new --repo MasumRab/EmailIntelligence "Set up GitHub Actions CI pipeline"

# Analysis tasks
jules new --repo MasumRab/EmailIntelligence "Analyze and document the agent configuration system"
```

## Authentication

```bash
# Login to Google/Jules (opens browser)
jules auth login

# Check authentication status
jules auth status

# Logout
jules logout

# Connect GitHub account (one-time)
# Visit https://jules.google.com to connect repositories
```

### Token-based Auth (CI/CD)

```bash
# For GitHub Actions or headless environments
jules auth login --token $JULES_API_TOKEN
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| "jules not found" | `npm install -g @google/jules` |
| "GitHub not connected" | Visit https://jules.google.com → Settings → Connect GitHub |
| "Repo not found" | Ensure repo is public or connected to Jules |
| "Rate limited" | Wait or use different Google account |

## References

- Full API: See [[jules-api]] for REST API details
- Workflows: See [[jules-workflows]] for patterns
- Sessions: See [[jules-sessions]] for local session analysis
