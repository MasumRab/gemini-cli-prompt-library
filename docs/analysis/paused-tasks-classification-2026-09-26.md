# Paused Tasks Classification — 2026-09-26

Generated from session store (1,446 sessions, synced 2026-09-26) + PR store
(3/4 repos fresh; EI live-checked via `gh pr view` — EI bulk sync 502'd on GitHub's side).

**Frozen session** = owner session in terminal state (COMPLETED/FAILED) while its PR
remains open/unmerged, or no session exists at all (orphan PR). Terminal ≠ dead —
`sendMessage` wakes COMPLETED/FAILED sessions; the wake-up must include the drift protocol.

---

## Class A — Live sessions awaiting steering (message now)

| Session | State | PR / Task | What's stuck |
|---|---|---|---|
| `14823980629961743161` | AWAITING | EI #732 (Bolt debounce) | PR CONFLICTING; also dup-family with #607 (APPROVED, session FAILED) and #792 |
| `6236298220428978887` | IN_PROGRESS | EI #832 (fix(ci) yaml syntax) | 1 failing check, mergeable UNKNOWN; session active Sept 25 |
| `445513471566265092` | AWAITING | Bolt perf agent, **no PR** | Created Sept 15, last update Sept 21 — work may be unlanded |
| `8371048452105557519` | AWAITING **since Apr 22** | kaggle #42 | **PR #42 already MERGED** — session is awaiting answers to questions that are moot |
| `9445754006296005497` | QUEUED | Bolt: Precision Performance | Updated 2026-09-26 06:53 UTC — moving, leave alone |
| `10304958435902448274` | QUEUED **since Apr 29** | kaggle_helper network timeout fix | Frozen queue, 5 months — nudge or close |

## Class B — Critical security PRs with FROZEN owner sessions (wake-up candidates)

Tier-1 security fixes, all still OPEN on EmailIntelligence main:

| PR | Severity | Live state | Owner session | Frozen type |
|---|---|---|---|---|
| #807 | CRITICAL (/token OAuth2Password) | OPEN **CONFLICTING** | `6253952775512400589` COMPLETED | Wake-up + drift protocol |
| #648 | CRITICAL (command injection, utility scripts) | OPEN CONFLICTING | `9976353698363073761` FAILED | Restore via sendMessage |
| #636 | CRITICAL (command injection, deployment) | OPEN MERGEABLE, **CHANGES_REQUESTED** | `14323196579621021860` FAILED | Restore; address review |
| #692/#609 | CRITICAL (command injection dup family) | OPEN CONFLICTING / CHANGES_REQUESTED | `9443413523109439597` / `3358543152461195241` both FAILED | Restore newest (#692) only |
| #645 | CRITICAL (memory exhaustion) | OPEN CONFLICTING | `2308156640503755864` FAILED | Restore |
| #795 | HIGH (insecure ML model deserialization) | OPEN CONFLICTING | `17325592108556266589` COMPLETED (also owns kaggle #95) | Wake-up + drift |
| #593/#597 | HIGH/MEDIUM (rate limiter memory DoS) | OPEN CONFLICTING | `9379951361616744672` / `17080630917374843345` FAILED | Restore one (#593) |
| #479 | HIGH (/token secure) | OPEN **MERGEABLE** | `9119171047628725306` FAILED | Restore → verify → merge |
| #853 | HIGH (weak security headers) | OPEN **MERGEABLE**, CI green | `18398192057925240698` COMPLETED Sept 21 | **Merge-ready — no session work needed** |
| #836 | path traversal (workflow manager) | OPEN CONFLICTING | `15182315018848459082` COMPLETED | Wake-up + drift |
| #605 | unsafe `echo -e` injection | OPEN CONFLICTING | `2847209926012702474` FAILED | Restore |
| #816 | MEDIUM (CORS + Git sanitization) | OPEN CONFLICTING | **no session** | Orphan → Class C |

## Class C — Orphan conflicted PRs (no session; manual worktree fix or new session)

| PR(s) | What | Live state |
|---|---|---|
| EI #777, #789, #794 | trunk-merge/pr-776 artifacts | OPEN, 15/15/8 failing checks — CI debris, decide delete vs salvage |
| EI #791, #778 | auto-merge pipeline fix (dup family) | OPEN CONFLICTING |
| EI #762, #788 | React.memo EmailList (dup family) | OPEN CONFLICTING |
| EI #626, #660 | uv bandit lint dup (sessions FAILED) | OPEN CONFLICTING, CHANGES_REQUESTED |
| EI #694, #691 | SonarQube REST integration dup | OPEN CONFLICTING |
| EI #467, #455 | Bolt Sort-First search dup | OPEN CONFLICTING |
| EI #623, #633 | Bolt pre-compile regex dup | OPEN CONFLICTING (623 APPROVED) |
| EI #607, #792 | Bolt debounce dup (732 has live session → steer that one) | OPEN CONFLICTING, #607 APPROVED |
| PL #26 | .gitignore update | OPEN, 8 failing, CHANGES_REQUESTED |

## Class D — Dup families, CI green, unmerged (pick one, close the rest)

| Family | PRs | CI | Sessions |
|---|---|---|---|
| kaggle: original prompt retrieval | #95, #104, #105, #109, #118 (5×) | all success | all COMPLETED → frozen |
| GL: TODO metadata cleanup | #383 (green) vs #370 (failing) | mixed | #383 COMPLETED, #370 FAILED |
| PL: scheduled-codebase-audit | #33, #45, #46, #47, #49, #50, #53, #55, #58, #59, #60, #62, #63 (13×!) | ~half failing | all COMPLETED → frozen |
| PL: #49/#50/#53 green subset | merge-ready candidates | success | frozen |

## Class E — Stale/frozen queue or moot

- `10304958435902448274` — QUEUED since Apr 29 (kaggle_helper timeout) — 5 months in queue is frozen; nudge once or close.
- `8371048452105557519` — AWAITING since Apr 22; its PR #42 is merged. Close out.
- GL #259/#264 — Sentinel CRITICAL/HIGH **drafts**, sessions COMPLETED, CI unknown — decide draft→open or drop.

---

## Recommended messages (priority order; 5+ min gaps for quota)

### Tier 1 — Critical security (send first)
1. **`9976353698363073761`** (FAILED, PR#648 CRITICAL): restore + drift-protocol conflict message
2. **`6253952775512400589`** (COMPLETED, PR#807 CRITICAL): wake-up + drift protocol (CONFLICTING)
3. **`14323196579621021860`** (FAILED, PR#636 CRITICAL): restore; MERGEABLE but CHANGES_REQUESTED — address review comments
4. **`9443413523109439597`** (FAILED, PR#692 CRITICAL dup): restore; close dup #609 after

### Tier 2 — Active progress
5. **`14823980629961743161`** (AWAITING, PR#732): conflict resolution + drift protocol; resolves family #607/#792
6. **`6236298220428978887`** (IN_PROGRESS, PR#832): status check + fix the 1 failing check
7. **`445513471566265092`** (AWAITING, no PR): status check — land work as PR or report findings

### Tier 3 — Close-outs and decisions (no session message needed for some)
8. **`8371048452105557519`**: "PR #42 merged — confirm remaining scope or close"
9. **PR#853**: MERGEABLE + CI green — merge directly, no session message
10. **PR#479**: restore `9119171047628725306`, verify, merge
11. kaggle dup family: pick best of #95/#104/#105/#109/#118, close other four (no wake needed — all green)
12. PL audit family: consolidate to one green PR (#49/#50/#53), close the other ten

### Leave alone
- `9445754006296005497` (QUEUED, updated today — moving)
- GL #259/#264 drafts — needs your draft→open decision first

Message templates: see memory `system/jules/session-management.md` (conflict-resolution
template with drift protocol, status-check template, wake-up template).
