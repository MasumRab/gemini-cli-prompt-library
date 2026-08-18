import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


class ArtefactWriter:
    def __init__(self, output_dir, write_legacy_aliases=True):
        self.output_dir = Path(output_dir)
        self.write_legacy_aliases = write_legacy_aliases

    def _normalise(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, list):
            return [self._normalise(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self._normalise(v) for k, v in obj.items()}
        return obj

    def write_json(self, filename, obj):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        path.write_text(
            json.dumps(self._normalise(obj), indent=2, sort_keys=True), encoding="utf-8"
        )
        return path

    def write_all(
        self, snapshot, relationship_graph, summary, execution_plan, triage_packets
    ):
        self.write_json("analysis_snapshot.json", snapshot)
        self.write_json("relationship_graph.json", relationship_graph)
        self.write_json("analysis_summary.json", summary)
        self.write_json("execution_plan.json", execution_plan)
        self.write_json("triage_packets.json", triage_packets)
        if self.write_legacy_aliases:
            legacy = Path(".graphite-agent")
            legacy.mkdir(parents=True, exist_ok=True)
            (legacy / "analysis_snapshot.json").write_text(
                json.dumps(self._normalise(snapshot), indent=2, sort_keys=True),
                encoding="utf-8",
            )
            (legacy / "plan.json").write_text(
                json.dumps(self._normalise(execution_plan), indent=2, sort_keys=True),
                encoding="utf-8",
            )
