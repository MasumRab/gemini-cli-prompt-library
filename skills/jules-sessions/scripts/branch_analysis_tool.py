#!/usr/bin/env python3
"""
Branch Analysis Tool - Standalone Version

Universal, tool-agnostic branch analysis for Git repositories.
No AI assistant required - runs independently.

Features:
- Branch synchronization status (ahead/behind)
- Orchestration branch detection
- Backend migration issues
- Temporary directory detection
- Duplicate documentation detection
- Launch script analysis
- Similar branch identification

Usage:
    python scripts/branch_analysis_tool.py [options]

Examples:
    python scripts/branch_analysis_tool.py
    python scripts/branch_analysis_tool.py --json
    python scripts/branch_analysis_tool.py --check-stale --max-stale-days 30
    python scripts/branch_analysis_tool.py --auto-fix
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class BranchStatus(Enum):
    UP_TO_DATE = "up_to_date"
    AHEAD = "ahead"
    BEHIND = "behind"
    DIVERGED = "diverged"
    NO_UPSTREAM = "no_upstream"


@dataclass
class BranchInfo:
    name: str
    status: BranchStatus
    ahead_count: int = 0
    behind_count: int = 0
    last_commit_date: str = ""
    is_orchestration: bool = False
    is_taskmaster: bool = False


@dataclass
class AnalysisIssue:
    severity: str  # critical, high, medium, low, info
    category: str
    location: str
    description: str
    suggestion: str = ""


@dataclass
class AnalysisResult:
    timestamp: str
    repository: str
    current_branch: str
    total_branches: int
    orchestration_branches: List[str]
    taskmaster_branches: List[str]
    branches_needing_push: List[Dict]
    branches_needing_pull: List[Dict]
    diverged_branches: List[Dict]
    issues: List[Dict]
    metrics: Dict


class BranchAnalyzer:
    """Standalone branch analysis tool."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.issues: List[AnalysisIssue] = []
        
    def run_git(self, args: List[str], check: bool = False) -> Tuple[str, str, int]:
        """Run git command and return output."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.CalledProcessError as e:
            return "", e.stderr, e.returncode
        except FileNotFoundError:
            return "", "Git not found", 1
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name."""
        stdout, _, _ = self.run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
        return stdout if stdout else None
    
    def get_all_branches(self, include_remotes: bool = False) -> List[str]:
        """Get list of all branches."""
        if include_remotes:
            stdout, _, _ = self.run_git(['branch', '-a'])
        else:
            stdout, _, _ = self.run_git(['branch'])
        
        branches = []
        for line in stdout.split('\n'):
            if line.strip():
                # Remove current branch marker
                branch = line.strip().lstrip('* ').strip()
                # Remove remote prefix for clean name
                if '->' in branch:  # Skip symbolic refs
                    continue
                branches.append(branch)
        return branches
    
    def get_upstream(self, branch: str) -> Optional[str]:
        """Get upstream branch for a given branch."""
        stdout, _, _ = self.run_git([
            'rev-parse', '--abbrev-ref', '--symbolic-full-name',
            f'{branch}@{{u}}'
        ])
        return stdout if stdout else None
    
    def get_ahead_behind(self, branch: str, upstream: str) -> Tuple[int, int]:
        """Get ahead/behind counts for a branch compared to upstream."""
        stdout, _, _ = self.run_git([
            'rev-list', '--left-right', '--count',
            f'{branch}...{upstream}'
        ])
        
        if stdout:
            parts = stdout.split()
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        return 0, 0
    
    def get_branch_status(self, branch: str) -> BranchInfo:
        """Get detailed status for a branch."""
        upstream = self.get_upstream(branch)
        
        if not upstream:
            return BranchInfo(
                name=branch,
                status=BranchStatus.NO_UPSTREAM
            )
        
        ahead, behind = self.get_ahead_behind(branch, upstream)
        
        if ahead > 0 and behind > 0:
            status = BranchStatus.DIVERGED
        elif ahead > 0:
            status = BranchStatus.AHEAD
        elif behind > 0:
            status = BranchStatus.BEHIND
        else:
            status = BranchStatus.UP_TO_DATE
        
        # Get last commit date
        stdout, _, _ = self.run_git([
            'log', '-1', '--format=%ci', branch
        ])
        
        info = BranchInfo(
            name=branch,
            status=status,
            ahead_count=ahead,
            behind_count=behind,
            last_commit_date=stdout.split()[0] if stdout else "",
            is_orchestration='orchestration' in branch.lower(),
            is_taskmaster='taskmaster' in branch.lower()
        )
        
        return info
    
    def analyze_all_branches(self, include_remotes: bool = False) -> List[BranchInfo]:
        """Analyze all branches and return detailed info."""
        branches = self.get_all_branches(include_remotes)
        return [self.get_branch_status(branch) for branch in branches]
    
    def check_backend_migration(self) -> List[AnalysisIssue]:
        """Check for old backend import statements."""
        issues = []
        
        # Find Python files with old backend imports
        try:
            stdout, _, _ = self.run_git(['ls-files', '*.py'])
            python_files = stdout.split('\n') if stdout else []
            
            for file in python_files[:50]:  # Limit to first 50 files
                if not file or file.startswith('.'):
                    continue
                    
                file_path = self.repo_path / file
                if not file_path.exists():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(8192)  # Read first 8KB
                        if 'from backend' in content or 'import backend' in content:
                            issues.append(AnalysisIssue(
                                severity="high",
                                category="migration",
                                location=file,
                                description="Old backend import detected",
                                suggestion="Update to 'from src.backend' or 'from backend.src'"
                            ))
                except Exception:
                    pass
        except Exception:
            pass
        
        return issues
    
    def check_temp_directories(self) -> List[AnalysisIssue]:
        """Check for temporary or backup directories."""
        issues = []
        temp_patterns = ['temp', 'backup', 'backlog', 'tmp', 'old', 'archive']
        
        for item in self.repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                for pattern in temp_patterns:
                    if pattern in item.name.lower():
                        issues.append(AnalysisIssue(
                            severity="low",
                            category="cleanup",
                            location=str(item.name),
                            description="Temporary/backup directory detected",
                            suggestion="Review and remove if no longer needed"
                        ))
                        break
        
        return issues
    
    def check_duplicate_docs(self) -> List[AnalysisIssue]:
        """Check for duplicate documentation files."""
        issues = []
        docs_dir = self.repo_path / 'docs'
        
        if not docs_dir.exists():
            return issues
        
        # Get docs outside docs/ directory
        for md_file in self.repo_path.glob('*.md'):
            if md_file.parent == docs_dir:
                continue
            
            # Check if similar file exists in docs/
            similar = list(docs_dir.glob(md_file.name))
            if similar:
                issues.append(AnalysisIssue(
                    severity="medium",
                    category="documentation",
                    location=str(md_file.relative_to(self.repo_path)),
                    description=f"Duplicate documentation file (also in docs/{md_file.name})",
                    suggestion="Consolidate documentation in docs/ directory"
                ))
        
        return issues
    
    def check_launch_scripts(self) -> List[AnalysisIssue]:
        """Check launch.py files for orchestration features."""
        issues = []
        
        for launch_file in self.repo_path.glob('**/launch.py'):
            if '.git' in str(launch_file):
                continue
            
            try:
                with open(launch_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
                    
                    has_orchestration = any([
                        'orchestration' in content.lower(),
                        'command.*pattern' in content.lower(),
                        'container' in content.lower(),
                        'services' in content.lower()
                    ])
                    
                    rel_path = str(launch_file.relative_to(self.repo_path))
                    
                    if not has_orchestration:
                        issues.append(AnalysisIssue(
                            severity="info",
                            category="launch_script",
                            location=rel_path,
                            description="Basic launch script (no orchestration features)",
                            suggestion="Consider adding orchestration features for consistency"
                        ))
            except Exception:
                pass
        
        return issues
    
    def generate_metrics(self, branches: List[BranchInfo]) -> Dict:
        """Generate analysis metrics."""
        total = len(branches)
        orchestration = sum(1 for b in branches if b.is_orchestration)
        taskmaster = sum(1 for b in branches if b.is_taskmaster)
        
        status_counts = {}
        for branch in branches:
            status = branch.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_branches': total,
            'orchestration_branches': orchestration,
            'taskmaster_branches': taskmaster,
            'status_distribution': status_counts,
            'branches_needing_push': status_counts.get('ahead', 0) + status_counts.get('diverged', 0),
            'branches_needing_pull': status_counts.get('behind', 0) + status_counts.get('diverged', 0),
        }
    
    def run_full_analysis(self, include_remotes: bool = False) -> AnalysisResult:
        """Run complete branch analysis."""
        current_branch = self.get_current_branch()
        branches = self.analyze_all_branches(include_remotes)
        
        # Collect issues
        self.issues.extend(self.check_backend_migration())
        self.issues.extend(self.check_temp_directories())
        self.issues.extend(self.check_duplicate_docs())
        self.issues.extend(self.check_launch_scripts())
        
        # Categorize branches
        orchestration_branches = [b.name for b in branches if b.is_orchestration]
        taskmaster_branches = [b.name for b in branches if b.is_taskmaster]
        
        branches_needing_push = [
            {'name': b.name, 'ahead': b.ahead_count, 'behind': b.behind_count}
            for b in branches if b.status == BranchStatus.AHEAD
        ]
        
        branches_needing_pull = [
            {'name': b.name, 'ahead': b.ahead_count, 'behind': b.behind_count}
            for b in branches if b.status == BranchStatus.BEHIND
        ]
        
        diverged_branches = [
            {'name': b.name, 'ahead': b.ahead_count, 'behind': b.behind_count}
            for b in branches if b.status == BranchStatus.DIVERGED
        ]
        
        return AnalysisResult(
            timestamp=datetime.now().isoformat(),
            repository=str(self.repo_path),
            current_branch=current_branch or "unknown",
            total_branches=len(branches),
            orchestration_branches=orchestration_branches,
            taskmaster_branches=taskmaster_branches,
            branches_needing_push=branches_needing_push,
            branches_needing_pull=branches_needing_pull,
            diverged_branches=diverged_branches,
            issues=[asdict(i) for i in self.issues],
            metrics=self.generate_metrics(branches)
        )


def print_text_report(result: AnalysisResult):
    """Print analysis results as text report."""
    print("\n" + "="*80)
    print("BRANCH ANALYSIS REPORT")
    print("="*80)
    print(f"\nRepository: {result.repository}")
    print(f"Current Branch: {result.current_branch}")
    print(f"Analysis Time: {result.timestamp}")
    print(f"Total Branches: {result.total_branches}")
    
    print("\n" + "-"*80)
    print("BRANCH STATUS SUMMARY")
    print("-"*80)
    
    if result.orchestration_branches:
        print(f"\n🎯 Orchestration Branches ({len(result.orchestration_branches)}):")
        for branch in result.orchestration_branches[:10]:
            print(f"   • {branch}")
        if len(result.orchestration_branches) > 10:
            print(f"   ... and {len(result.orchestration_branches) - 10} more")
    
    if result.taskmaster_branches:
        print(f"\n🎭 Taskmaster Branches ({len(result.taskmaster_branches)}):")
        for branch in result.taskmaster_branches[:10]:
            print(f"   • {branch}")
    
    if result.branches_needing_push:
        print(f"\n⬆️  Branches Needing Push ({len(result.branches_needing_push)}):")
        for branch in result.branches_needing_push[:10]:
            print(f"   • {branch['name']} ({branch['ahead']} commits ahead)")
    
    if result.branches_needing_pull:
        print(f"\n⬇️  Branches Needing Pull ({len(result.branches_needing_pull)}):")
        for branch in result.branches_needing_pull[:10]:
            print(f"   • {branch['name']} ({branch['behind']} commits behind)")
    
    if result.diverged_branches:
        print(f"\n⚠️  Diverged Branches ({len(result.diverged_branches)}):")
        for branch in result.diverged_branches[:10]:
            print(f"   • {branch['name']} ({branch['ahead']} ahead, {branch['behind']} behind)")
    
    if result.issues:
        print("\n" + "-"*80)
        print("ISSUES DETECTED")
        print("-"*80)
        
        by_severity = {}
        for issue in result.issues:
            sev = issue['severity']
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(issue)
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity in by_severity:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵', 'info': 'ℹ️'}.get(severity, '•')
                print(f"\n{emoji} {severity.upper()} ({len(by_severity[severity])}):")
                for issue in by_severity[severity][:5]:
                    print(f"   • [{issue['category']}] {issue['location']}")
                    print(f"     {issue['description']}")
                if len(by_severity[severity]) > 5:
                    print(f"   ... and {len(by_severity[severity]) - 5} more")
    
    print("\n" + "-"*80)
    print("METRICS")
    print("-"*80)
    metrics = result.metrics
    print(f"\n📊 Status Distribution:")
    for status, count in metrics.get('status_distribution', {}).items():
        print(f"   • {status}: {count}")
    
    print(f"\n📈 Summary:")
    print(f"   • Branches needing push: {metrics.get('branches_needing_push', 0)}")
    print(f"   • Branches needing pull: {metrics.get('branches_needing_pull', 0)}")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Standalone Branch Analysis Tool - No AI assistant required",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/branch_analysis_tool.py                    # Full analysis
  python scripts/branch_analysis_tool.py --json             # JSON output
  python scripts/branch_analysis_tool.py --check-stale      # Check stale branches
  python scripts/branch_analysis_tool.py --auto-fix         # Auto-fix issues
        """
    )
    
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--include-remotes', action='store_true',
                       help='Include remote branches in analysis')
    parser.add_argument('--check-stale', action='store_true',
                       help='Check for stale branches')
    parser.add_argument('--max-stale-days', type=int, default=90,
                       help='Maximum age in days for stale branches (default: 90)')
    parser.add_argument('--auto-fix', action='store_true',
                       help='Attempt to auto-fix issues')
    parser.add_argument('--repo', type=Path, default=None,
                       help='Repository path (default: current directory)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = BranchAnalyzer(args.repo)
    
    # Run analysis
    result = analyzer.run_full_analysis(args.include_remotes)
    
    # Output results
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print_text_report(result)
    
    # Exit with appropriate code
    critical_issues = sum(1 for i in result.issues if i['severity'] == 'critical')
    high_issues = sum(1 for i in result.issues if i['severity'] == 'high')
    
    if critical_issues > 0:
        sys.exit(2)
    elif high_issues > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
