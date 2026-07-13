import json
from pathlib import Path
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()

def run_id():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')

def rj(p, d=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else d

def wj(p, x):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2))

def wt(p, text):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def run_dirs(base='.graphite-agent/outputs', rid=None):
    rid = rid or run_id()
    base = Path(base)
    run = base / 'runs' / rid
    latest = base / 'latest'
    run.mkdir(parents=True, exist_ok=True)
    latest.mkdir(parents=True, exist_ok=True)
    return rid, run, latest

def write_run_json(name, obj, rid=None, base='.graphite-agent/outputs'):
    rid, run, latest = run_dirs(base, rid)
    obj = dict(obj)
    obj.setdefault('run_id', rid)
    wj(run / name, obj)
    wj(latest / name, obj)
    return rid, run / name

def write_run_text(name, text, rid=None, base='.graphite-agent/outputs'):
    rid, run, latest = run_dirs(base, rid)
    wt(run / name, text)
    wt(latest / name, text)
    return rid, run / name
