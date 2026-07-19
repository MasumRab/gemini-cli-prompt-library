#!/bin/bash
set -euo pipefail

# Jules Environment Setup Script
# Installs development tools and configures the environment for the Jules repo.
#
# Usage:
#   ./setup_jules_env.sh             # Full setup (unified)
#   ./setup_jules_env.sh --compact   # Compact setup (skip optional tools)

export DEBIAN_FRONTEND=noninteractive

# --- Mode detection ---
COMPACT=false
for arg in "$@"; do
    case "$arg" in
        --compact) COMPACT=true ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

# --- Sandbox / noninteractive detection ---
# Set NONINTERACTIVE_SANDBOX=1 to skip all sudo/apt-get blocks.
# This is the default in CI containers, Kaggle kernels, and other
# restricted shells where sudo is unavailable or network egress is limited.
NONINTERACTIVE_SANDBOX="${NONINTERACTIVE_SANDBOX:-0}"

# sandbox() guards every sudo/apt-get / system-package block.
#   $1 = mode: "exit" | "skip"  (exit = error+stop,  skip = warn+continue)
#   $2 = human-readable description (for log messages)
# All remaining args become the command to run inside a subshell.
sandbox() {
  local mode="${1:?Usage: sandbox <exit|skip> <description> <cmd...>}"
  shift
  local desc="$1"
  shift

  local log_prefix="[sandbox]"
  local available=1

  # sudo must exist and be callable (NOPASSWD or root session)
  if ! command -v sudo &>/dev/null; then
    available=0
  elif ! sudo -n true 2>/dev/null; then
    available=0
  fi

  # apt-get must also be present (covers minimal container images)
  if ! command -v apt-get &>/dev/null; then
    available=0
  fi

  if [ "$available" -eq 1 ]; then
    # Shell-check note: we intentionally bypass set -e for guarded blocks
    # so a single failing package does not abort the whole sandbox flow.
    set +e
    sudo "$@"
    local rc=$?
    set -e
    return $rc
  fi

  # --- sandbox / no-sudo path ---
  if [ "$mode" = "exit" ]; then
    echo "${log_prefix} ERROR: $desc — no sudo/apt-get available" >&2
    echo "${log_prefix} Re-run this script with NONINTERACTIVE_SANDBOX=0 (requires root)" >&2
    exit 1
  fi

  echo "${log_prefix} SKIPPING: $desc (no sudo/apt-get)" >&2
  return 0
}

# --- PATH setup (must come before the uv bootstrap step so we can
#     execute uv in the same noninteractive shell without sourcing .bashrc) ---
if [ -z "${PATH##*$HOME/.local/bin*}" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# --- Bootstrap uv ---
# Official Astral install script is noninteractive by default — no TTY or sudo needed.
# Installs to $HOME/.local/bin/uv and $HOME/.local/bin/uvx.
if ! command -v uv &>/dev/null; then
  echo "[info] uv not found — bootstrapping from astral.sh"
  curl -LsSf https://astral.sh/uv/install.sh | env CARGO_HOME="$HOME/.cargo" sh
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "[info] uv already available at $(command -v uv)"
fi

# --- System packages ---
  sandbox skip "system packages (jq ripgrep curl wget build-essential)" \
    bash -c "apt-get update -qq && sudo apt-get install -y -qq jq ripgrep curl wget build-essential"

# --- yq (pinned version) ---
YQ_VERSION="v4.44.1"
if ! command -v yq &>/dev/null; then
  sandbox skip "yq $YQ_VERSION" \
    bash -c 'wget -qO /usr/local/bin/yq "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64" && sudo chmod +x /usr/local/bin/yq'
else
  echo "[info] yq already available at $(command -v yq)"
fi

# --- GitHub CLI (official GPG-verified source) ---
if ! command -v gh &>/dev/null; then
  sandbox skip "gh: download GPG key" \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
  sandbox skip "gh: add apt repo" \
    bash -c 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null'
  sandbox skip "gh: apt-get install" \
    bash -c 'sudo apt-get update -qq && sudo apt-get install gh -y -qq'
else
  echo "[info] gh already available at $(command -v gh)"
fi

# --- Node.js 20 LTS (via NodeSource signed repo) — skipped in compact mode ---
if [ "$COMPACT" = false ]; then
  if ! command -v node &>/dev/null; then
    sandbox skip "Node.js 20 LTS" \
      bash -c 'curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs -qq'
  else
    echo "[info] node already available at $(command -v node)"
  fi
fi

# --- Global npm tools — skipped in compact mode ---
if [ "$COMPACT" = false ]; then
  if command -v node &>/dev/null && command -v npm &>/dev/null; then
    sandbox skip "global npm tools (graphite-cli ast-grep)" \
      sudo npm i -g @withgraphite/graphite-cli @ast-grep/cli
  else
    echo "[sandbox] SKIPPING: global npm tools (node/npm not available)" >&2
  fi
fi

# --- Python tools ---
python3 -m pip install uv pre-commit -q

# --- PATH persistence ---
B='export PATH="$HOME/.local/bin:$PATH"'
grep -qF "$B" ~/.bashrc 2>/dev/null || echo "$B" >> ~/.bashrc

echo "Environment setup complete. Run: source ~/.bashrc"
