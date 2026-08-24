import json
import os
import sys
import time
import urllib.request

API = "https://jules.googleapis.com/v1alpha"
KEY = os.environ["JULES_API_KEY"]

# The 11 known nonterminal sessions
NONTERMINAL = [
    "7404018986702295062",  # AWAITING_USER_FEEDBACK
    "10304958435902448274",  # QUEUED
    "14844012706076784544",  # AWAITING_USER_FEEDBACK
    "18254541687978082373",  # IN_PROGRESS
    "5824169116591251349",  # AWAITING_USER_FEEDBACK
    "11760979078520753675",  # AWAITING_USER_FEEDBACK
    "5852715954766644480",  # AWAITING_USER_FEEDBACK
    "6052746651524889133",  # AWAITING_USER_FEEDBACK
    "647582418723672708",  # AWAITING_USER_FEEDBACK
    "17065719860896443446",  # IN_PROGRESS
    "9445754006296005497",  # QUEUED
]


def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": KEY})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def get_session(sid):
    """Get session details"""
    try:
        return fetch_json(f"{API}/sessions/{sid}")
    except Exception as e:
        return {"error": str(e)}


def get_activities(sid, max_pages=3):
    """Get activities, only last page(s) to save bandwidth"""
    all_acts = []
    url = f"{API}/sessions/{sid}/activities?pageSize=50"
    for _ in range(max_pages):
        try:
            data = fetch_json(url, timeout=20)
        except Exception as e:
            return all_acts, str(e)
        acts = data.get("activities", [])
        all_acts.extend(acts)
        # Check if there's a next page
        next_token = data.get("nextPageToken")
        if not next_token:
            break
        url = f"{API}/sessions/{sid}/activities?pageSize=50&pageToken={next_token}"
        time.sleep(0.5)
    return all_acts, None


def classify_activity(act):
    """Extract meaningful info from an activity"""
    originator = act.get("originator", "?")
    ts = act.get("createTime", "?")
    content = {}
    text = ""

    for key in act:
        if key in ("name", "createTime", "originator", "id"):
            continue
        val = act[key]
        if isinstance(val, dict):
            if "agentMessage" in val:
                text = val["agentMessage"][:500]
                content["type"] = "agent_message"
            elif "userMessage" in val:
                text = val["userMessage"][:500]
                content["type"] = "user_message"
            elif "planGenerated" in val or "plan" in val:
                content["type"] = "plan_generated"
                plan = val.get("planGenerated", val.get("plan", {}))
                steps = plan.get("steps", [])
                content["plan_steps"] = len(steps)
                if steps:
                    content["plan_step_titles"] = [
                        s.get("title", "")[:100] for s in steps[:5]
                    ]
            elif "artifacts" in val:
                content["type"] = "artifacts"
                arts = val["artifacts"]
                content["artifact_count"] = len(arts) if isinstance(arts, list) else 1
            else:
                content["type"] = key
                content["keys"] = list(val.keys())[:5]
        elif isinstance(val, list):
            content["type"] = key
            content["count"] = len(val)
        else:
            content["type"] = key
            content["value"] = str(val)[:200]

    content["text"] = text
    content["originator"] = originator
    content["timestamp"] = ts
    return content


results = {}
for i, sid in enumerate(NONTERMINAL):
    print(f"[{i+1}/{len(NONTERMINAL)}] Processing {sid}...", file=sys.stderr)

    session = get_session(sid)
    activities, act_err = get_activities(sid)

    # Classify last 10 meaningful activities
    classified = [classify_activity(a) for a in activities[-15:]]

    results[sid] = {
        "session": {
            "name": session.get("name", ""),
            "state": session.get("state", "UNKNOWN"),
            "title": session.get("title", ""),
            "repoUrl": session.get("repoUrl", ""),
            "baseBranch": session.get("baseBranch", ""),
            "createdTime": session.get("createdTime", session.get("createTime", "")),
            "updatedTime": session.get("updatedTime", session.get("updateTime", "")),
        },
        "activity_count": len(activities),
        "activity_error": act_err,
        "last_activities": classified,
    }
    time.sleep(1)  # Rate limit courtesy

# Save results
with open("/tmp/nonterminal_classification.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
