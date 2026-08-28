import json
from pathlib import Path


class ExecutionPlanReader:
    def __init__(self, path=".graphite-agent/outputs/execution_plan.json"):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            raise RuntimeError(f"Missing execution plan: {self.path}")
        return json.loads(self.path.read_text(encoding="utf-8"))
