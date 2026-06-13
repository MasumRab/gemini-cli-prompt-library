#!/usr/bin/env python3
"""Record target-scoped decisions."""
import argparse
import json
from agent_core import record_decision

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--question')
    p.add_argument('--branch')
    p.add_argument('--choice')
    p.add_argument('--reason')
    a = p.parse_args()
    ev = record_decision(a.question, a.branch, a.choice, a.reason, supersedes=None, event_type='target_decision')
    print(json.dumps(ev, indent=2))

if __name__ == '__main__':
    main()
