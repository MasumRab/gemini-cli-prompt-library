# State transitions among Jules sessions we messaged

Generated 2026-09-27. Messaged set = session IDs in `skills/jules-sessions/references/sent_responses.md`
∪ sessions with a `userMessaged` activity in `~/.jules/store.db`.

**Messaged sessions: 144** (curated log 112, API userMessaged 42, union 144).

## Current state of messaged sessions

| State | Count |
|---|---:|
| COMPLETED | 70 |
| FAILED | 67 |
| QUEUED | 2 |
| AWAITING_USER_FEEDBACK | 2 |
| NOT-IN-STORE | 1 |
| UNKNOWN | 1 |
| IN_PROGRESS | 1 |

## Transitions — baseline 2026-08-06 snapshot → now

Observed in both snapshots: **47** of 144 messaged sessions.

| Transition | Count |
|---|---:|
| FAILED → FAILED | 21 |
| working → working | 15 |
| working → FAILED | 10 |
| FAILED → working | 1 |

**Flips: 11** (23% of observed).

| Session | From | To | update_time |
|---|---|---|---|
| `16994837303056291039` | COMPLETED | FAILED | 2026-08-12T19:15:42 |
| `13172420826211369022` | COMPLETED | FAILED | 2026-08-12T19:16:32 |
| `16638769467548151530` | COMPLETED | FAILED | 2026-08-12T19:16:35 |
| `3927471279591052912` | COMPLETED | FAILED | 2026-08-12T19:16:42 |
| `7979893028704332984` | COMPLETED | FAILED | 2026-08-12T19:16:45 |
| `14586978430582998057` | COMPLETED | FAILED | 2026-08-12T19:17:01 |
| `8364650927851285109` | COMPLETED | FAILED | 2026-08-12T19:20:36 |
| `7592875515078415283` | COMPLETED | FAILED | 2026-08-12T19:20:44 |
| `2088004130054247653` | FAILED | COMPLETED | 2026-09-12T13:42:41 |
| `18095420007057529466` | COMPLETED | FAILED | 2026-09-14T11:49:40 |
| `2079450350875343630` | COMPLETED | FAILED | 2026-09-25T13:25:02 |

## The 2026-08-12/13 batch is the epicenter

34 sessions were messaged in that batch. Eight of them were COMPLETED on 2026-08-06 and are FAILED now —
every one with an `update_time` inside **2026-08-12T19:15–19:20Z**, the exact send window. Four other batch
sessions that were COMPLETED on 08-06 are still COMPLETED, with `update_time` on 08-14 or 08-28 — outside the send window.

## Observed sequence (one session, live activity log)

`14586978430582998057`:

```
2026-04-30T18:24:51  sessionCompleted
2026-08-12T19:15:58  userMessaged  "Session completed. Please confirm final state and close out."
2026-08-12T19:17:01  state -> FAILED   (63 s after the message; message is the last activity)
```

The message is the final activity and the state flips to FAILED 63 s later, with no agent reply. This is a
**temporal correlation on a single session**, not an established causal mechanism. The reasons a Jules session
fails are not yet understood — the flip may be caused by the wake-up itself, by sandbox/VM provisioning on
re-run, by the repo state at that moment, or by something else entirely. Treat this as an open question.

## Correction (user, 2026-09-27)

Two points that override the framing above:

1. **The complexity of the reasons for failure is not yet understood.** Do not present a mechanism as settled.
2. **Completion is not a final state.** A COMPLETED session is still wakeable and re-runnable, so there is
   **no reason for any close-out message to be sent at all** — not merely "close-out messages are risky".
   Close-out steering should be removed from the message vocabulary entirely.

