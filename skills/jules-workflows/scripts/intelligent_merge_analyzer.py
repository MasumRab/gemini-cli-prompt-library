#!/usr/bin/env python3
"""
intelligent_merge_analyzer.py - Analyze change overlap between branches

Usage:
    python3 intelligent_merge_analyzer.py <file> <local_range> <remote_range>

Example:
    python3 intelligent_merge_analyzer.py src/core/security.py origin/BRANCH..HEAD origin/BRANCH~10..origin/BRANCH
"""

import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class OverlapAnalysis:
    file_path: str
    local_only_lines: int
    remote_only_lines: int
    overlapping_lines: int
    total_changed_lines: int
    overlap_percent: float
    recommendation: str


def run_command(cmd: str) -> str:
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


def get_changed_lines(file_path: str, commit_range: str) -> Set[int]:
    """Get line numbers that changed in a commit range"""
    try:
        diff = run_command(f"git diff {commit_range} -- {file_path}")
        changed_lines = set()

        for line in diff.split("\n"):
            if line.startswith("@@"):
                # Parse @@ -X,Y +Z,W @@ format
                parts = line.split("+")
                if len(parts) > 1:
                    # Get the +Z,W part
                    location = parts[1].split(" ")[0]
                    if "," in location:
                        start = int(location.split(",")[0])
                        count = int(location.split(",")[1])
                    else:
                        start = int(location)
                        count = 1

                    for i in range(start, start + count):
                        changed_lines.add(i)

        return changed_lines
    except Exception as e:
        print(f"Error getting changed lines: {e}")
        return set()


def analyze_overlap(
    file_path: str, local_range: str, remote_range: str
) -> OverlapAnalysis:
    """Analyze overlap between local and remote changes"""

    # Get changed lines in each version
    local_lines = get_changed_lines(file_path, local_range)
    remote_lines = get_changed_lines(file_path, remote_range)

    # Find overlaps
    overlapping = local_lines & remote_lines
    local_only = local_lines - remote_lines
    remote_only = remote_lines - local_lines
    total = local_lines | remote_lines

    overlap_percent = (len(overlapping) / len(total) * 100) if total else 0

    # Determine recommendation
    if overlap_percent < 20:
        recommendation = "✅ LOW OVERLAP - Safe to auto-merge"
    elif overlap_percent < 50:
        recommendation = "⚠️ MODERATE OVERLAP - Review recommended, likely safe"
    elif overlap_percent < 75:
        recommendation = "⚠️ HIGH OVERLAP - Manual review required"
    else:
        recommendation = "❌ VERY HIGH OVERLAP - Manual resolution required"

    return OverlapAnalysis(
        file_path=file_path,
        local_only_lines=len(local_only),
        remote_only_lines=len(remote_only),
        overlapping_lines=len(overlapping),
        total_changed_lines=len(total),
        overlap_percent=overlap_percent,
        recommendation=recommendation,
    )


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python3 intelligent_merge_analyzer.py <file> <local_range> <remote_range>"
        )
        print("")
        print("Arguments:")
        print("  file         - Path to file to analyze")
        print(
            "  local_range  - Git range for local changes (e.g., origin/BRANCH..HEAD)"
        )
        print(
            "  remote_range - Git range for remote changes (e.g., origin/BRANCH~10..origin/BRANCH)"
        )
        print("")
        print("Example:")
        print(
            "  python3 intelligent_merge_analyzer.py src/core/security.py origin/BRANCH..HEAD origin/BRANCH~10..origin/BRANCH"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    local_range = sys.argv[2]
    remote_range = sys.argv[3]

    # Verify file exists
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    print("=" * 60)
    print("Intelligent Merge Analyzer")
    print("=" * 60)
    print(f"File: {file_path}")
    print(f"Local range: {local_range}")
    print(f"Remote range: {remote_range}")
    print("")

    # Analyze overlap
    analysis = analyze_overlap(file_path, local_range, remote_range)

    # Print results
    print(f"=== Analysis Results ===")
    print(f"Lines changed in local only:  {analysis.local_only_lines}")
    print(f"Lines changed in remote only: {analysis.remote_only_lines}")
    print(f"Overlapping changes:          {analysis.overlapping_lines}")
    print(f"Total changed lines:          {analysis.total_changed_lines}")
    print(f"Overlap percentage:           {analysis.overlap_percent:.1f}%")
    print("")
    print(f"Recommendation: {analysis.recommendation}")
    print("")

    # Detailed breakdown
    print("=== Detailed Breakdown ===")
    if analysis.overlap_percent < 20:
        print("✅ Most changes are non-overlapping.")
        print("   Git's auto-merge should handle this cleanly.")
        print("   Manual review recommended but not required.")
    elif analysis.overlap_percent < 50:
        print("⚠️ Some overlap detected.")
        print("   Review the merged result carefully.")
        print("   Most changes should be compatible.")
    elif analysis.overlap_percent < 75:
        print("⚠️ Significant overlap detected.")
        print("   Manual review is REQUIRED.")
        print("   Some conflicts may need resolution.")
    else:
        print("❌ High overlap detected.")
        print("   Manual resolution is REQUIRED.")
        print("   Expect conflicts in overlapping areas.")

    print("")
    print("=== Suggested Action ===")
    if analysis.overlap_percent < 20:
        print("1. git merge origin/BRANCH --no-ff -m 'merge: Combine changes'")
        print("2. Review git diff --cached")
        print("3. git commit -m 'merge: Intelligently combined changes'")
    elif analysis.overlap_percent < 50:
        print("1. git merge origin/BRANCH --no-ff -m 'merge: Combine changes'")
        print("2. Check for conflicts: git status")
        print("3. If conflicts, use: git mergetool")
        print("4. Review merged result carefully")
        print("5. git commit -m 'merge: Combined changes with manual review'")
    else:
        print("1. python3 intelligent_merger.py " + file_path + " HEAD origin/BRANCH")
        print("2. Review the .merged output file")
        print("3. Manually resolve conflicts")
        print("4. Replace original: mv " + file_path + ".merged " + file_path)
        print("5. git add " + file_path)
        print("6. git commit -m 'merge: Manual resolution of conflicting changes'")

    print("")
    print("=" * 60)


if __name__ == "__main__":
    main()
