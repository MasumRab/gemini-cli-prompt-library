# Deep Research Improved Prompt

## Objective
Conduct a thorough, evidence-based investigation of the target directory/repository. Avoid the common failure modes identified in prior audits: empty-directory false negatives, documentation-vs-reality mismatches, and speculative claims.

## Mandatory Pre-Flight Checks
1. **Target validation**: Confirm the exact target path, directory name, and repository exists before searching. If multiple similar names exist (e.g., `.graphite-agent` vs `.graphite-agents`), list all candidates and ask for clarification if ambiguous.
2. **Working directory confirmation**: Print the current working directory and list its contents before starting. Do not assume `/tmp/deep-research-*` is the target.
3. **Source-of-truth order**: Inspect in this order:
   - Local filesystem (glob, read, grep)
   - Remote repository tree (GitHub API / git tree)
   - Documentation files (README, docs/, IMPLEMENTATION_REPORT)
   - Tests and CI configs
   Do not skip earlier steps to jump to external repos.

## Investigation Rules
- **Do not invent files**: If a directory is empty, report that explicitly as a finding, not as a failure.
- **Cross-check every path**: Before citing a file, verify it exists with `glob` or `read`. If `read` returns ENOENT, do not cite it.
- **Version reconciliation**: If docs mention versions (v64, v72, v73) but fixtures are missing, report the discrepancy explicitly and check whether the version is implemented elsewhere (scripts/, tools/, tests/).
- **Count verification**: Before stating "N tools" or "N outputs," enumerate the actual directory contents. Report both the claimed count and the actual count side by side.
- **Test verification**: Before claiming tests exist, `glob` the tests directory and `read` the test files. Report actual class names, method names, and line counts.
- **Architecture accuracy**: Distinguish between thin wrapper scripts, orchestrator modules, and shared libraries. Do not describe a centralized monolith as "N independent tools" without evidence.

## Output Format
For each version or component investigated, report:
1. **Existence**: Does it exist on disk? Exact path.
2. **Files**: Complete list of files with sizes and one-line descriptions.
3. **Tests**: Exact test file paths, class names, method names, and assertion counts.
4. **Documentation**: Which docs reference it, and whether those docs match reality.
5. **Gaps**: Unimplemented features, empty outputs, missing fixtures, or stub documentation.
6. **Confidence**: High / Medium / Low, with explicit gaps.

## Edge Cases
- Empty directories: Report as "directory exists but contains no files" — this is a valid finding.
- Missing fixtures: Distinguish between "not yet implemented" and "intentionally omitted."
- Conflicting docs: Flag the conflict, identify which source is authoritative, and recommend a resolution.
- External repos: Only inspect external repos if local inspection is exhausted. Clearly separate local findings from external findings.

## Anti-Patterns to Avoid
- Do not conclude "no test coverage" without enumerating the tests directory.
- Do not describe a directory as "fixture-only" without checking for executable code, scripts, or entry points.
- Do not cite file paths that have not been verified with `read` or `glob`.
- Do not present speculative tradeoffs (Path A/B/C/D) without grounding them in actual file-level evidence.
- Do not treat `/tmp` sandbox failures as evidence about the target repository.

## Validation Step
Before finalizing the report:
1. Re-read every file path cited in the report and confirm it exists.
2. Re-check every count (tools, outputs, tests) against actual directory listings.
3. Confirm that every "missing" item was actually searched for and not just assumed absent.
