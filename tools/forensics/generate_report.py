#!/usr/bin/env python3
"""
Generate forensics report for a target repository.

Usage:
    python3 tools/forensics/generate_report.py \
        --repo EmailIntelligence \
        --type failure_analysis \
        --session-id 596003508416904399 \
        --output workspaces/EmailIntelligence/analysis/forensics/
"""

import argparse
import os
import sys
import yaml
from datetime import datetime, timezone

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.jules_api_client import JulesAPIClient


def generate_frontmatter(session_id, title, repo, report_type):
    """Generate YAML frontmatter for forensics report."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return {
        'session': {
            'id': str(session_id),
            'title': title,
            'repository': repo,
            'created': now,
            'updated': now,
            'status': 'completed',
            'source': 'forensics'
        },
        'forensics': {
            'type': report_type,
            'confidence': 'probable',
            'api_boundary': 'https://jules.googleapis.com/v1alpha',
            'retrieval_timestamp': now
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Generate forensics report')
    parser.add_argument('--repo', required=True, help='Target repository name')
    parser.add_argument('--type', required=True, 
                        choices=['failure_analysis', 'intervention_outcome', 
                                 'pattern_analysis', 'audit', 'investigation'],
                        help='Report type')
    parser.add_argument('--session-id', help='Jules session ID')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--title', help='Report title')
    args = parser.parse_args()

    # Determine output path
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    filename = f"{args.type}_{date_str}.md"
    output_path = os.path.join(args.output, filename)

    # Create output dir
    os.makedirs(args.output, exist_ok=True)

    # Generate frontmatter
    title = args.title or f"{args.type.replace('_', ' ').title()} Report"
    frontmatter = generate_frontmatter(
        args.session_id or 'N/A', 
        title, 
        args.repo,
        args.type
    )

    # Create report content
    content = '---\n' + yaml.dump(frontmatter, default_flow_style=False, sort_keys=False) + '---\n\n'
    content += f"# {title}\n\n"
    content += f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    content += f"**Repository:** {args.repo}\n"
    content += f"**Type:** {args.type}\n"
    content += f"**Session:** {args.session_id or 'N/A'}\n\n"
    content += "## Summary\n\n[TODO: Add summary]\n\n"
    content += "## Findings\n\n[TODO: Add findings]\n\n"
    content += "## Recommendations\n\n[TODO: Add recommendations]\n\n"

    # Write report
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Generated: {output_path}")
    
    # Update INDEX.yaml if exists
    index_path = os.path.join(args.output, 'INDEX.yaml')
    if os.path.exists(index_path):
        print(f"NOTE: Update {index_path} to include new report")


if __name__ == '__main__':
    main()
