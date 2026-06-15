#!/usr/bin/env python3
import argparse
from agent_core import explain_branch

p = argparse.ArgumentParser()
p.add_argument("--branch", required=True)
a = p.parse_args()
print(explain_branch(a.branch))
