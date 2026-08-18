import json
from pathlib import Path


class GuidedTriage:
    def __init__(self, output_dir=".graphite-agent/outputs"):
        self.output_dir = Path(output_dir)

    def _load(self, filename):
        path = self.output_dir / filename
        if not path.exists():
            raise RuntimeError(f"Missing file: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def relationship_index(self):
        return {
            edge["id"]: edge
            for edge in self._load("relationship_graph.json").get("edges", [])
        }

    def print_summary(self):
        summary = self._load("analysis_summary.json")
        print(json.dumps(summary.get("counts", {}), indent=2))
        return summary

    def print_packets(self):
        triage = self._load("triage_packets.json")
        rel = self.relationship_index()
        for packet in triage.get("packets", {}).values():
            print("=" * 72)
            print(f"Triage packet: {packet['id']}")
            print(f"Branch: {packet['branch']}")
            print(f"Status: {packet['status']}")
            print(f"Reason: {packet.get('primary_reason')}")
            print(f"Recommendation: {packet.get('recommended_action')}")
            for rel_id in packet.get("relationship_edges", []):
                edge = rel.get(rel_id)
                edge_type = edge.get("edge_type") if edge else "missing"
                print(f"  - {rel_id}: {edge_type}")
        return triage
