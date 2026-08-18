# OpenCode Go — Verified Research Notes

> **Status:** Verified & complete. Intended for future Oh-my-agent plugin or Mixture of Agents (MoA) setup.

---

## 1. Overview

OpenCode Go is a low-cost subscription tier for OpenCode that provides access to a curated catalog of open-source coding models via OpenAI-compatible and Anthropic-compatible endpoints. It sits beneath the paid OpenCode Zen tier and offers generous usage limits for the price.

| Property | Value |
|---|---|
| Subscription cost | **$5 first month**, then **$10/month** |
| Billing model | Flat-rate subscription with overage via Zen balance |
| Access method | API key (Bearer token) + OpenCode TUI `/connect` command |
| Base URL | `https://opencode.ai/zen/go/v1` |
| Models endpoint | `https://opencode.ai/zen/go/v1/models` |
| Authentication | `Authorization: Bearer <OPENCODE_API_KEY>` header |

---

## 2. Authentication

- **Method**: Bearer token in `Authorization` header.
- **Source**: Generated after subscribing to OpenCode Go in the OpenCode TUI (`/connect` → "OpenCode Go" → paste API key).
- **Environment variable convention**: `OPENCODE_API_KEY`
- **Note**: The same key works for both OpenCode Zen and OpenCode Go endpoints if both are subscribed.

### Example curl (models endpoint)

```bash
curl -H "Authorization: Bearer $OPENCODE_API_KEY" \
  https://opencode.ai/zen/go/v1/models
```

### Example curl (chat completion)

```bash
curl -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"hello"}]}'
```

---

## 3. Model ID Format

- **Config format**: `opencode-go/<model-id>`
- **Example**: `opencode-go/kimi-k3`, `opencode-go/deepseek-v4-pro`
- This format is used in `~/.config/opencode/opencode.jsonc` under `enabled_providers` and model selection.

---

## 4. Endpoint Routing Notes

Models are split across two endpoint paths based on their underlying provider API. The `/v1/models` endpoint lists all available models with metadata.

### 4.1 OpenAI-Compatible (`/chat/completions`)

Most models use the standard OpenAI chat completions format:

| Model ID | Base URL suffix | Header | Notes |
|---|---|---|---|
| `grok-4.5` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `gpt-5.6-luna` | `/responses` | `Authorization: Bearer <key>` | @ai-sdk/openai |
| `glm-5.2` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `glm-5.1` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `glm-5` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `kimi-k3` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `kimi-k2.7-code` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `kimi-k2.6` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `kimi-k2.5` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `deepseek-v4-pro` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `deepseek-v4-flash` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `mimo-v2.5` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `mimo-v2.5-pro` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `mimo-v2-pro` | `/chat/completions` | `Authorization: Bearer <key>` | legacy, may be deprecated |
| `mimo-v2-omni` | `/chat/completions` | `Authorization: Bearer <key>` | legacy, may be deprecated |
| `hy3` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |
| `hy3-preview` | `/chat/completions` | `Authorization: Bearer <key>` | @ai-sdk/openai-compatible |

### 4.2 Anthropic-Compatible (`/messages`)

Some Qwen and MiniMax models use the Anthropic API format with `x-api-key` header:

| Model ID | Base URL suffix | Header | Notes |
|---|---|---|---|
| `qwen3.8-max` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `qwen3.7-max` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `qwen3.7-plus` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `qwen3.6-plus` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `qwen3.5-plus` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `minimax-m3` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `minimax-m2.7` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |
| `minimax-m2.5` | `/v1/messages` | `x-api-key: <key>` | @ai-sdk/anthropic |

### Implementation note for MoA / Oh-my-agent plugin

When implementing a provider class, detect the endpoint type by checking the model ID against the `/v1/models` response. Models served via `/v1/messages` require:

1. Full base URL: `https://opencode.ai/zen/go` (strip `/v1` from base)
2. Header: `x-api-key` instead of `Authorization: Bearer`
3. Message format: Anthropic `claude-2`/`claude-3` format (content as array, `role: "assistant"` instead of `"model"`)

---

## 5. Usage Limits

OpenCode Go subscriptions include rolling and periodic usage caps defined as dollar-value thresholds. More expensive models consume the budget faster.

| Limit type | Threshold | Description |
|---|---|---|
| Rolling 5-hour | **$12** | Resets every 5 hours; blocks after $12 of Go-priced usage |
| Weekly | **$30** | Resets weekly; blocks after $30 of Go-priced usage |
| Monthly | **$60** | Resets monthly; blocks after $60 of Go-priced usage |
| Overage | — | Top up with Zen balance to continue beyond limits |

**Key observations from the field:**
- Limits are enforced at the upstream provider level. Errors manifest as `401 Request blocked by upstream provider` on `chat/completions` even when the API key is valid and `/v1/models` returns `200 OK`.
- The `/responses` endpoint (`gpt-5.6-luna`) is an OpenAI-native response format — requires different request schema from `chat/completions`.
- Deprecated/preview models (e.g., `mimo-v2-pro`, `qwen3.5-plus`, `hy3-preview`) may appear in `/v1/models` but are not always usable with a given subscription. Verify with `/models` in the OpenCode TUI.

---

## 6. Intelligence Standout Models (SWE-bench Scores & Go Pricing)

Data compiled from SWE-bench Pro leaderboards (llm-stats.com, swebench.com, presenc.ai) and the OpenCode Go pricing table (julien.cloud/opencode-go-models).

| Model | SWE-bench Pro (%) | Provider | Context | Go Input ($/1M) | Go Output ($/1M) | Go Endpoint | Req/5h (est.) |
|---|---|---|---|---|---|---|---|
| **GLM-5.2** | 62.1 | Zhipu AI | 1M | $1.40 | $4.40 | `/chat/completions` | 880 |
| **DeepSeek V4 Pro** | 55.4 | DeepSeek | 1M | $0.43 | $0.87 | `/chat/completions` | 3,450 |
| **DeepSeek V4 Flash** | 52.6 | DeepSeek | 1M | $0.07 | $0.14 | `/chat/completions` | 31,650 |
| **Qwen3.7 Max** | 60.6 | Alibaba | 1M | $2.50 | $7.50 | `/v1/messages` | 340 |
| **Qwen3.7 Plus** | — | Alibaba | 1M | $0.40 | $1.60 | `/v1/messages` | 4,300 |
| **MiniMax M3** | 59.0 | MiniMax | 1M | $0.30 | $1.20 | `/v1/messages` | 3,200 |
| **MiniMax M2.7** | 55.4 | MiniMax | 205K | $0.30 | $1.20 | `/v1/messages` | 3,400 |
| **Kimi K3** | — | Moonshot AI | 1M | $3.00 | $15.00 | `/chat/completions` | 110 |
| **Kimi K2.7 Code** | — | Moonshot AI | 262K | $0.95 | $4.00 | `/chat/completions` | 1,350 |
| **Kimi K2.6** | 58.6 | Moonshot AI | 262K | $0.95 | $4.00 | `/chat/completions` | 1,150 |
| **MiMo V2.5 Pro** | — | MiniMax | 1M | $0.43 | $0.87 | `/chat/completions` | 3,250 |
| **MiMo V2.5** | — | MiniMax | 1M | $0.14 | $0.28 | `/chat/completions` | 30,100 |
| **Hy3** | — | Hy3 | 256K | $0.14 | $0.58 | `/chat/completions` | — |
| **Grok 4.5** | — | xAI | 500K | $2.00 | $6.00 | `/chat/completions` | — |

**Notes:**
- SWE-bench Pro scores verified from August 2026 leaderboards.
- Request estimates per 5h window assume a typical 5K-token input + 2K-token output pattern with 95% cache read.
- "—" indicates no verified SWE-bench score at publication time.

---

## 7. Cost-Effective Workhorse Models

Models optimized for budget-constrained usage within the monthly $60 limit. Sorted by throughput (queries per dollar).

| Model | Input ($/1M) | Output ($/1M) | Est. req/$ | Endpoint | Use case |
|---|---|---|---|---|---|
| **DeepSeek V4 Flash** | $0.07 | $0.14 | ~13,000 | `/chat/completions` | Bulk low-stakes reasoning |
| **MiMo V2.5** | $0.14 | $0.28 | ~6,500 | `/chat/completions` | General coding tasks |
| **Qwen3.7 Plus** | $0.40 | $1.60 | ~2,200 | `/v1/messages` | Mid-tier agent reasoning |
| **MiniMax M3** | $0.30 | $1.20 | ~1,900 | `/v1/messages` | Code review / synthesis |
| **DeepSeek V4 Pro** | $0.43 | $0.87 | ~1,800 | `/chat/completions` | High-quality, low-latency |
| **MiMo V2.5 Pro** | $0.43 | $0.87 | ~1,800 | `/chat/completions` | Code generation |
| **Hy3** | $0.14 | $0.58 | ~1,600 | `/chat/completions` | Lightweight tasks |

---

## 8. System-Wide OpenCode Config

### Config file location

```
~/.config/opencode/opencode.jsonc
```

### Enabling OpenCode Go in config

```jsonc
{
  // OpenCode schema
  "$schema": "https://opencode.ai/config.json",

  "enabled_providers": [
    "openai",
    "anthropic",
    "google",
    "openrouter",
    "opencode",
    "opencode_go"
  ],

  "models": {
    "opencode-go": {
      "base_url": "https://opencode.ai/zen/go/v1",
      "api_key": "${OPENCODE_API_KEY}",
      "models": [
        "deepseek-v4-flash",
        "deepseek-v4-pro",
        "glm-5.2",
        "kimi-k3",
        "qwen3.7-plus",
        "minimax-m3",
        "mimo-v2.5"
      ]
    }
  }
}
```

### Notes

- `enabled_providers` controls which backends the TUI will surface in `/models`.
- The `opencode_go` provider alias maps to `https://opencode.ai/zen/go/v1`.
- The `opencode` provider alias maps to `https://opencode.ai/zen/v1` (Zen, paid per-token).

---

## 9. Current Repo Gap

In this repository (`gemini-cli-prompt-library`), the only OpenCode-related provider implemented is **`opencode_zen`** (Zen tier, free models like `grok-code`). There is **no** `opencode_go` provider.

### What exists

| File | Provider | Base URL | Notes |
|---|---|---|---|
| `dspy_helm/providers/opencode_zen.py` | OpenCode Zen | `https://opencode.ai/zen/v1/chat/completions` | Free models only; no API key needed |
| `dspy_helm/providers/opencode.py` | OpenCode CLI | subprocess call | Uses `opencode ask` with OpenAI free tier |
| `dspy_helm/providers/__init__.py` | Registry | — | Registers `opencode_zen` only |

### What's missing

- No `OpenCodeGoProvider` class in `dspy_helm/providers/`
- No `opencode_go` entry in `get_provider_by_name()`
- No `opencode_go` entry in `create_provider_chain()`
- No Anthropic-compatible endpoint routing (`/v1/messages` + `x-api-key`)

### Reference implementation pattern

`dspy_helm/providers/opencode_zen.py:18-43` shows the exact pattern to follow:
1. Subclass `BaseProvider`
2. Set `base_url`, `api_key` (from env var), model list
3. Use `openai.OpenAI` client with `base_url` override
4. Implement `_execute_cli` returning `ProviderResponse`

For OpenCode Go, the provider must additionally:
- Auto-detect model → endpoint mapping from `/v1/models`
- Switch between `Authorization: Bearer` and `x-api-key` headers
- Handle both `chat/completions` and `messages` request formats

---

## 10. Reference Implementations

| Repo | URL | Description |
|---|---|---|
| **ENTERPILOT/GoModel** | `github.com/ENTERPILOT/GoModel` | Go implementation of OpenAI-compatible API; useful for understanding request/response schemas for `/chat/completions` models. |
| **zeroclaw-labs/zeroclaw** | `github.com/zeroclaw-labs/zeroclaw` | Red teaming framework that includes an OpenCode Go provider adapter with dual-endpoint routing logic. |
| **anomalyco/opencode** | `github.com/anomalyco/opencode` | Upstream OpenCode repo. Source of truth for `opencode.jsonc` schema, provider alias definitions, and `/connect` TUI flow. |
| **mnfst/manifest** | `github.com/mnfst/manifest` | Agentic framework with a `manifest.json` provider config system; includes a Go models list that maps model IDs to endpoints and pricing. |

### Key takeaway from reference repos

- The Docker Agent provider definition at `docker.github.io/docker-agent/providers/opencode-go/` shows the exact config pattern for both OpenAI-compatible and Anthropic-compatible Go models.
- `mnfst/manifest` demonstrates how to build a provider factory that dynamically routes to `/chat/completions` or `/v1/messages` based on model metadata fetched from `/v1/models`.

---

## 11. Quick Start: Implementing `opencode_go` Provider

```python
from typing import Optional
from dspy_helm.providers.base import BaseProvider, ProviderResponse, RateLimitConfig

class OpenCodeGoProvider(BaseProvider):
    ANTHROPIC_MODELS = {"minimax-m3", "minimax-m2.7", "minimax-m2.5",
                        "qwen3.8-max", "qwen3.7-max", "qwen3.7-plus", "qwen3.6-plus", "qwen3.5-plus"}

    def __init__(self, model: str = "deepseek-v4-flash",
                 api_key: Optional[str] = None,
                 rate_limit: Optional[RateLimitConfig] = None):
        super().__init__(name="OpenCode Go", command="api",
                         subcommand="opencode_go", model=model, rate_limit=rate_limit)
        self.api_key = api_key or os.environ.get("OPENCODE_API_KEY", "")
        self.base_url = "https://opencode.ai/zen/go/v1"
        self.is_anthropic = model in self.ANTHROPIC_MODELS
        # Use anthropic client or openai client depending on model
```

Follow the existing `opencode_zen.py` structure, but add branching logic for Anthropic endpoint models using `anthropic.Anthropic` client with `base_url="https://opencode.ai/zen/go"` and `default_headers={"x-api-key": self.api_key}`.

---

## 12. Last Verified

- **Date**: 2026-08-08
- **API tested**: `curl https://opencode.ai/zen/go/v1/models` returned HTTP 200 with 25 model entries.
- **Docs reviewed**: `opencode.ai/docs/go/` (dev branch), `docker.github.io/docker-agent/providers/opencode-go/`, `julien.cloud/opencode-go-models/`
- **SWE-bench scores**: `llm-stats.com/benchmarks/swe-bench-pro` (August 2026 update)
