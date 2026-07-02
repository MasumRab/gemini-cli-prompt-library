import json
from pathlib import Path
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def rj(p, d=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else d


def wj(p, x):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2))
