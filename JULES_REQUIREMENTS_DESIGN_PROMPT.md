# Prompt to Generate Jules-Version Requirements and Design Documents

## Objective
Instruct Jules to generate its own canonical versions of REQUIREMENTS.md and DESIGN.md for the taskmaster branch alignment work, based on its analysis and understanding, so these can be downloaded and compared with the rough scaffold versions in scratch_branch_alignment_scaffold/.

## Context
The files in scratch_branch_alignment_scaffold/ (REQUIREMENTS.md, DESIGN.md, PRD_BRANCH_ALIGNMENT.md) were created as a preliminary scaffold for investigation. Jules session 596003508416904399 has completed the discovery and analysis phase and has developed a detailed understanding of:
- The isolated nature of the origin/taskmaster branch
- The locations of correct tooling (in main-rooted branches that mistakenly contained taskmaster work)
- The state preserved in future_advanced_state/
- The required next steps for implementation

## Recommended Message to Send to Jules
Send this message to an active Jules session (or use it to create a new session focused on documentation generation):

```
Please generate canonical REQUIREMENTS.md and DESIGN.md documents for the taskmaster branch alignment work based on your analysis from session 596003508416904399 and the investigation in scratch_branch_alignment_scaffold/. 

For REQUIREMENTS.md:
- Extract and formalize the hard constraints (REQ-01 through REQ-08) that you've identified as necessary for safe and correct execution
- Include any additional requirements you've discovered during your analysis
- Format as a clear, numbered list of requirements with brief explanations where needed

For DESIGN.md:
- Document the system architecture and components as you understand them
- Include the start state diagram (D-1) with actual SHAs and branch relationships you've discovered
- Document the engine wiring (D-2) with specific file references and command structures
- Detail the target matrix (D-3) showing allowed integration directions and gates
- Include signal processing, safety invariants, and merge discipline rules (D-4 through D-7)
- Use the actual findings from your branch analysis, rogue work discovery, and tooling location identification

These documents should represent your current, canonical understanding based on the completed analysis phase. They will be used for comparison with the rough scaffold versions to validate alignment and identify any gaps or improvements needed in our shared understanding.
```

## How to Use This Prompt

### Option 1: Send to Existing Session
If you have an active Jules session you want to use for this documentation work:
```bash
python tools/sessions/jules_send_message.py <SESSION_ID> "$(cat JULES_REQUIREMENTS_DESIGN_PROMPT.md)"
```

### Option 2: Create New Session for Documentation Generation
```bash
# First, get the repository URL for EmailIntelligence (adjust as needed)
REPO_URL="https://github.com/MasumRab/EmailIntelligence"

# Create a new session focused on documentation generation
SESSION_ID=$(python -c "
import os
import sys
sys.path.insert(0, 'tools')
from tools.api.jules_api_client import JulesAPIClient
client = JulesAPIClient()
session = client.create_session({
    'prompt': open('JULES_REQUIREMENTS_DESIGN_PROMPT.md').read(),
    'source': {'github': '$REPO_URL', 'baseBranch': 'main'},
    'autoPr': False
})
print(session['name'])
")

echo "Created session $SESSION_ID for documentation generation"
echo "Monitor progress with: python tools/sessions/jules_list_activities.py $SESSION_ID --full"
```

## Expected Jules Output

Based on the PRD_BRANCH_ALIGNMENT.md "Step-to-file responsibility map", Jules is expected to create/update specific files during its work. For documentation generation, Jules would likely:

1. **Create/update DESIGN.md** during Step S1 (Bootstrap & start state):
   - File: DESIGN.md (specifically sections D-1/D-2)
   - Action: create if missing; update start-state gate
   - Content: Would include the start state diagram with actual discovered SHAs, engine wiring details, etc.

2. **REQUIREMENTS.md handling**: While not explicitly listed in the Jules-owned files, Jules would likely:
   - Reference and validate against requirements during validation gating (REQ-04, PRD R0.3, S3)
   - Potentially create a requirements traceability matrix or validation ruleset
   - The REQUIREMENTS.md document might be considered an input that Jules works with rather than creates

## Retrieving Generated Documents

Once Jules has processed your message and generated the documents, you can retrieve them using standard Git operations once they're committed to the branch, or by:

1. **Checking the session activities** for file creation/modification events:
   ```bash
   python tools/sessions/jules_list_activities.py <SESSION_ID> --full | grep -i "created\|modified\|updated"
   ```

2. **Monitoring for specific document mentions** in Jules messages:
   ```bash
   python tools/sessions/jules_list_activities.py <SESSION_ID> --full | grep -i "requirements\|design"
   ```

3. **Once committed to branch**: Standard Git checkout/show operations

## Comparison Process

After Jules generates the documents:
1. Download/compare the Jules-generated REQUIREMENTS.md with scratch_branch_alignment_scaffold/REQUIREMENTS.md
2. Download/compare the Jules-generated DESIGN.md with scratch_branch_alignment_scaffold/DESIGN.md
3. Note any differences in:
   - Specific requirements identified
   - Architectural understanding
   - Technical details (SHAs, file paths, command structures)
   - Gaps or additional insights in either version
4. Use the comparison to refine the shared understanding and update the canonical documents as needed

## Important Notes

- Jules session 596003508416904399 is currently in a **completed state** and would need to be restarted or a new session created for this work
- The documents Jules generates would reflect its analysis-based understanding from the completed discovery phase
- This approach ensures we get Jules' "canonical" view based on its actual investigation work
- The comparison will help align our shared understanding and improve the documentation quality
