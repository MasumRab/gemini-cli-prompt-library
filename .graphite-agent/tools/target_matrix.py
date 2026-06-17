#!/usr/bin/env python3
"""Query target matrix."""
import argparse
import json
from pathlib import Path
from agent_core import read_json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branch')
    a = p.parse_args()
    matrix = read_json(Path('.graphite-agent/outputs/target_matrix.json'))
    if a.branch:
        print(json.dumps(matrix.get('branches', {}).get(a.branch, {}), indent=2))
    else:
        print(json.dumps(matrix, indent=2))

if __name__ == '__main__':
    main()
