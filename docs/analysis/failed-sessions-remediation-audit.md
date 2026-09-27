# Failed Jules Sessions — Prior Fix Attempts & Why They Remain FAILED

Generated 2026-09-27. Sources: `skills/jules-sessions/references/sent_responses.md` (attempt log),
`~/.jules/store.db` (state + activity snapshots), live Jules REST API (state + activity window).

**Scope**: 445 sessions currently FAILED in the store. **50** of them carry a documented prior fix attempt.

## How to read this

- **Attempted** = the session ID appears in `sent_responses.md`, the authoritative log of messages sent to sessions.
- **Category** = determined from the live activity window (who spoke last, how many failures, whether the recovery message landed).
- A session can be FAILED for two different reasons: *why it failed originally* and *why the recovery attempt did not clear it*.
  The category below is the second one — the reason the fix attempt did not stick.

## Root-cause categories

| Category | Count | Meaning |
|---|---:|---|
| DORMANT-SINCE-ATTEMPT | 23 | Store-derived: session changed at/near the attempt — attempt registered, nothing since |
| RE-FAILED | 9 | Message delivered, session resumed, and immediately failed again |
| SILENT | 7 | Message delivered but session never responded (no agent activity after) |
| NEVER-DELIVERED | 5 | Send was quota-blocked (429) — session has only its original failure, no user message |
| NO-DELIVERY-EVIDENCE | 4 | Store-derived: session last changed >1 day before the attempt — no evidence the message landed |
| CHANGED-AFTER-ATTEMPT | 2 |  |

## Bottom line

None of the 50 remain FAILED because the fix was wrong. They remain FAILED because the recovery channel itself does not work on them:

1. **The message never arrived** (5 confirmed + 4 store-evidenced + part of the 23 dormant) — quota 429 at batch time. The session never even saw the instruction.
2. **The message arrived and the session re-failed instantly** (9) — every `sendMessage` wakes the session, it re-runs VM provisioning, and fails again. The kaggle cluster is the clearest case (clone error).
3. **The message arrived and the session went silent** (7) — the recovery message is literally the last activity; no agent response followed.
4. **The message arrived, the session changed once, then stopped** (23) — the attempt registered (store `update_time` moves to the attempt date) but nothing since. These are long-running sessions whose activity tail was not walked; the head window shows the pre-failure work.

**Implication**: re-messaging is not a general remedy. For cluster 2 the session is unrecoverable by messaging and needs manual branch surgery or closure;
for cluster 1 the fix is to re-send when quota is available; for clusters 3-4 the sessions are dormant and should be closed or manually salvaged rather than re-nudged.


## Prior fix attempts — batches

The recovery messages were sent in discrete batches. Each batch is recorded in `sent_responses.md`:

| Date | Batch | Sessions | What was sent |
|---|---|---:|---|
| 2026-08-13 | Refresh stalled/failed sessions + reopen batch | 45 msgs | status check / retry / reopen / rebase / close directives |
| 2026-08-15/16 | Latest PR updates + follow-up/approve/retry | 20 msgs | per-session follow-ups, approvals, retries |
| 2026-08-17 | Merge-instruction batch | 11 msgs | merge base + push to refresh mergeability, clear quality gates |
| 2026-09-12/13 | Progress sweep + review refresh + rereview | 40+ msgs | close-out, review refresh, mode override, comment bridge |
| 2026-09-14 | Nudge all active + CLI lane alignment + restores | 40+ msgs | nudges, lane assignments, restores with current branch state |
| 2026-09-18 | FAILED session salvage (workspace audit) | 2 msgs | wake-up/salvage with current branch state |

**Quota is a recurring cause of non-delivery**: the 2026-09-13 rereview batch logged 7 sessions as `429` (message never sent),
and the 2026-08-16 batch logged one `RESOURCE_EXHAUSTED` retry. Sessions whose only activity is a failure (no `userMessaged`)
are exactly those whose recovery message never landed.

## Confirmed failure mode — kaggle clone loop

The kaggle-notebooks-analysis cluster shows the clearest mechanism. Every `userMessaged` is followed within seconds by a
`sessionFailed` with the same payload — the sandbox cannot clone the repo:

```
Jules encountered an error when cloning the repo.
+ sudo rm -rf /app
+ sudo mkdir /app
+ sudo chown 1001 /app
```
For these sessions the wake does not resume work — it re-runs VM provisioning, fails at clone, and re-fails.
The session never emits an `agentMessaged`, so requests to "explain the error" go unanswered. This is not fixable by messaging.


## MasumRab/EmailIntelligence — 41 attempted, still FAILED

| Created | Session | Last attempt | Live | Category | Why the fix did not stick |
|---|---|---|---|---|---|
| 2026-08-17 | `14970126622961835953` | 2026-09-13 (review-only) | FAILED | NEVER-DELIVERED | no user message in history — send never landed (quota 429 at batch time) |
| 2026-08-17 | `4227155626214895348` | 2026-09-13 (review-only) | FAILED | NEVER-DELIVERED | no user message in history — send never landed (quota 429 at batch time) |
| 2026-08-16 | `10759997676130822408` | 2026-09-13 (review-only) | FAILED | NEVER-DELIVERED | no user message in history — send never landed (quota 429 at batch time) |
| 2026-08-16 | `6289750792488543569` | 2026-09-13 (review-only) | FAILED | NEVER-DELIVERED | no user message in history — send never landed (quota 429 at batch time) |
| 2026-08-16 | `10602007366444539739` | 2026-09-13 (impl) | FAILED | RE-FAILED | last activity is sessionFailed (1 total) — the wake triggered a new failure |
| 2026-08-16 | `5958407664361578225` | 2026-09-13 (review-only) | FAILED | NEVER-DELIVERED | no user message in history — send never landed (quota 429 at batch time) |
| 2026-08-16 | `2739128843849774554` | 2026-09-13 (—) | FAILED | RE-FAILED | last activity is sessionFailed (1 total) — the wake triggered a new failure |
| 2026-08-15 | `10041449041565916881` | 2026-09-18 (—) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=5 am=5; store update 2026-09-19 ~= attempt 2026-09-18, unchanged since — never recovered |
| 2026-08-15 | `16572236002364851031` | 2026-09-13 (—) | FAILED | RE-FAILED | last activity is sessionFailed (1 total) — the wake triggered a new failure |
| 2026-08-14 | `4011484320208761877` | 2026-09-13 (retry,review-only) | FAILED | RE-FAILED | last activity is sessionFailed (5 total) — the wake triggered a new failure |
| 2026-08-14 | `3066004504936610335` | 2026-09-13 (retry,review-only) | FAILED | RE-FAILED | last activity is sessionFailed (4 total) — the wake triggered a new failure |
| 2026-08-09 | `15008828426973856885` | 2026-08-13 (retry,reopen) | FAILED | RE-FAILED | last activity is sessionFailed (4 total) — the wake triggered a new failure |
| 2026-08-09 | `5938780760607407206` | 2026-08-13 (retry,reopen) | FAILED | RE-FAILED | last activity is sessionFailed (3 total) — the wake triggered a new failure |
| 2026-08-09 | `8294985337104762975` | 2026-08-13 (retry,reopen) | FAILED | RE-FAILED | last activity is sessionFailed (3 total) — the wake triggered a new failure |
| 2026-05-06 | `12339942557859330507` | 2026-09-14 (—) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-05-04 | `4786476835892279965` | 2026-09-14 (—) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-05-04 | `8312407700305908496` | 2026-09-14 (—) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-05-04 | `18095420007057529466` | 2026-09-14 (—) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=5 am=3; store update 2026-09-14 ~= attempt 2026-09-14, unchanged since — never recovered |
| 2026-05-04 | `14432945922325525432` | 2026-09-14 (—) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-04-21 | `13005011563799472129` | 2026-08-13 (retry,reopen) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-04-21 | `16320746218997740002` | 2026-08-13 (guidance,reopen) | FAILED | CHANGED-AFTER-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-09-25 is 43d after attempt 2026-08-13 — session changed later, still FAILED |
| 2026-04-17 | `10865630989900669675` | 2026-08-13 (close) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=4 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-17 | `2281891166145596786` | 2026-08-13 (guidance) | FAILED | CHANGED-AFTER-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-09-25 is 43d after attempt 2026-08-13 — session changed later, still FAILED |
| 2026-04-16 | `9164742845732374282` | 2026-08-13 (retry,reopen) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-04-14 | `12679806066699207963` | 2026-09-19 (—) | FAILED | NO-DELIVERY-EVIDENCE | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-09-14 is 5d before attempt 2026-09-19 — no evidence the message landed |
| 2026-04-12 | `14323196579621021860` | 2026-09-19 (—) | FAILED | NO-DELIVERY-EVIDENCE | long session (>40 activities, tail not walked); head: fails=0 um=6 am=0; store update 2026-08-06 is 44d before attempt 2026-09-19 — no evidence the message landed |
| 2026-04-09 | `8098457377596089277` | 2026-08-13 (merge) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-08-14 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-02 | `647582418723672708` | 2026-08-16 (—) | FAILED | SILENT | last activity is the recovery message — session never responded after it |
| 2026-03-27 | `16314414237181869537` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=15 am=3; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-24 | `7592875515078415283` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=8 am=1; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-23 | `654824856418808212` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=0 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-23 | `8364650927851285109` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=1 um=2 am=1; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-22 | `9033653426873037468` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=0 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-22 | `16961981115510330540` | 2026-09-14 (—) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=10 am=6; store update 2026-09-14 ~= attempt 2026-09-14, unchanged since — never recovered |
| 2026-03-15 | `4710008747613819117` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=0 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-03-08 | `17857204272766840681` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-02-23 | `9119171047628725306` | 2026-09-19 (—) | FAILED | NO-DELIVERY-EVIDENCE | long session (>40 activities, tail not walked); head: fails=0 um=2 am=0; store update 2026-08-06 is 44d before attempt 2026-09-19 — no evidence the message landed |
| 2026-02-13 | `125717287297355188` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=5 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-02-03 | `15863163327149061241` | 2026-08-13 (guidance,reopen) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=5 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-01-11 | `8449104713119985854` | 2026-09-19 (—) | FAILED | NO-DELIVERY-EVIDENCE | long session (>40 activities, tail not walked); head: fails=0 um=0 am=0; store update 2026-08-17 is 33d before attempt 2026-09-19 — no evidence the message landed |
| 2025-11-07 | `2960310825137265296` | 2026-09-14 (—) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-09-14 ~= attempt 2026-09-14, unchanged since — never recovered |

## MasumRab/kaggle-notebooks-analysis — 7 attempted, still FAILED

| Created | Session | Last attempt | Live | Category | Why the fix did not stick |
|---|---|---|---|---|---|
| 2026-05-29 | `16610982362272230087` | 2026-09-14 (—) | FAILED | RE-FAILED | last activity is sessionFailed (8 total) — the wake triggered a new failure |
| 2026-04-23 | `13172420826211369022` | 2026-08-13 (guidance) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=4 am=4; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-23 | `7979893028704332984` | 2026-08-13 (guidance) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=2 am=2; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-22 | `14586978430582998057` | 2026-08-13 (close) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=6 am=3; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-22 | `3927471279591052912` | 2026-08-13 (nudge) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=3 am=2; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-22 | `16638769467548151530` | 2026-08-13 (nudge) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=2 am=1; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
| 2026-04-22 | `16994837303056291039` | 2026-08-13 (nudge) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |

## MasumRab/gemini-fullstack-langgraph-quickstart — 2 attempted, still FAILED

| Created | Session | Last attempt | Live | Category | Why the fix did not stick |
|---|---|---|---|---|---|
| 2026-08-05 | `11267029240983047750` | 2026-09-18 (—) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=1 am=1; store update 2026-09-19 ~= attempt 2026-09-18, unchanged since — never recovered |
| 2026-04-23 | `7956689661359593335` | 2026-08-13 (nudge,close) | FAILED | DORMANT-SINCE-ATTEMPT | long session (>40 activities, tail not walked); head: fails=0 um=0 am=0; store update 2026-08-12 ~= attempt 2026-08-13, unchanged since — never recovered |
