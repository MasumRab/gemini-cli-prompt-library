import os
import re

output_dir = 'docs/tasks/graphite_linear'

# 1. Migrate Root Health from Phase 4 to Phase 5
p4_path = os.path.join(output_dir, '4_V72_TARGET_INTENT.md')
p5_path = os.path.join(output_dir, '5_STACKING_STRATEGY.md')

if os.path.exists(p4_path) and os.path.exists(p5_path):
    with open(p4_path, 'r') as f: p4_content = f.read()
    with open(p5_path, 'r') as f: p5_content = f.read()

    # Blocks to move (Root Health specifics)
    root_blocks = re.findall(r'(## .*?(?:root_health|root_refresh|root_questions|root_decide).*?)(?=\n## |\Z)', p4_content, re.DOTALL)
    new_p4 = p4_content
    for b in root_blocks:
        new_p4 = new_p4.replace(b, '')

    # Append to P5 before the 'Expected Outcome' or at the end
    insertion_point = '## 5.19 Expected Outcome'
    if insertion_point in p5_content:
        new_p5 = p5_content.replace(insertion_point, '\n'.join(root_blocks) + '\n\n' + insertion_point)
    else:
        new_p5 = p5_content + '\n\n' + '\n'.join(root_blocks)

    with open(p4_path, 'w') as f: f.write(new_p4)
    with open(p5_path, 'w') as f: f.write(new_p5)

# 2. Prune V7.2 tools from Phase 3
p3_path = os.path.join(output_dir, '3_V71_FRAMEWORK.md')
if os.path.exists(p3_path):
    with open(p3_path, 'r') as f: p3_content = f.read()

    v72_tools = [
        'discover_targets.py', 'target_analyse.py', 'target_questions.py',
        'target_decide.py', 'target_matrix.py', 'retarget_rework.py', 'validate_targets.py'
    ]

    new_p3 = p3_content
    for tool in v72_tools:
        new_p3 = re.sub(r'\.graphite-agent/tools/' + re.escape(tool) + r'\n?', '', new_p3)

    with open(p3_path, 'w') as f: f.write(new_p3)

# 3. Standardize Decision Logic in Phase 8
p8_path = os.path.join(output_dir, '8_SYSTEM_GLUE_AND_PLUMBING.md')
if os.path.exists(p8_path):
    with open(p8_path, 'r') as f: p8_content = f.read()

    decision_glue = '''
## 8.6 Universal Decision Interface

To ensure consistency across Parent, Target, and Root layers, implement a common interface for all 'decide' tools.

**Mandatory CLI Arguments:**
- `--branch <name>` or `--target <name>`: The subject of the decision.
- `--choice <value>`: The machine-readable decision (e.g., `parent=main`, `target=orchestration-tools`).
- `--reason <text>`: Human-readable rationale (required).
- `--supersedes <event_id>`: (Optional) The ID of a previous decision this choice replaces.

**Shared Logic:**
1.  Load `outputs/decision_log.jsonl`.
2.  Generate a unique `event_id`.
3.  Append the new JSON object to the log.
4.  Trigger `tools/rebuild_plan.py` to project the new state.
'''

    if '8.6 Universal Decision Interface' not in p8_content:
        with open(p8_path, 'a') as f: f.write(decision_glue)

print('Final alignment complete.')
