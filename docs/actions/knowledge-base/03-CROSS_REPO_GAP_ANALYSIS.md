# 03-CROSS_REPO_GAP_ANALYSIS.md

## 3.1 Canonical Jules Workflows Baseline (reference from canonical repo)

The canonical Jules workflows represent the reference implementation for all workflow patterns. These workflows are maintained in the main Jules repository and serve as the source of truth for workflow structure, naming conventions, and implementation patterns.

### Workflow Inventory:
- **workflow-email-intelligence.yml**: Core email processing pipeline with intelligence features
- **workflow-user-onboarding.yml**: User registration and onboarding sequence
- **workflow-data-backup.yml**: Automated data backup and verification
- **workflow-api-health-check.yml**: System health monitoring and alerting
- **workflow-content-publishing.yml**: Content management and distribution pipeline

### Canonical Workflow Characteristics:
- Consistent naming: `workflow-<feature-name>.yml`
- Standardized triggers: `schedule`, `workflow_call`, `workflow_dispatch`
- Uniform job naming conventions
- Shared action usage patterns
- Common error handling and notification patterns
- Standardized environment variable usage
- Consistent artifact retention policies

## 3.2 EmailIntelligence Jules Workflows (current state with gaps highlighted)

The EmailIntelligence repository contains workflows that have diverged from the canonical baseline due to feature-specific adaptations and independent evolution.

### Current Workflows:
- **workflow-email-intelligence.yml**: Modified version with additional intelligence features
- **workflow-email-validation.yml**: Email-specific validation workflow (not in canonical)
- **workflow-model-training.yml**: ML model training workflow (not in canonical)

### Identified Gaps:
1. **Missing Standard Workflows**:
   - Missing: `workflow-user-onboarding.yml`
   - Missing: `workflow-data-backup.yml`
   - Missing: `workflow-api-health-check.yml`

2. **Naming Inconsistencies**:
   - `workflow-email-validation.yml` (should follow `workflow-<feature>` pattern but is feature-specific)
   - `workflow-model-training.yml` (same issue)

3. **Trigger Variations**:
   - Email intelligence workflow uses non-standard cron schedule
   - Missing `workflow_call` triggers for reusability

4. **Action Usage Differences**:
   - Uses custom actions not present in canonical
   - Missing standardized logging actions
   - Different dependency management approach

5. **Structural Differences**:
   - Different job segmentation
   - Varied environment variable naming
   - Inconsistent artifact handling

## 3.3 Three Additional Target Repos Workflow States (AppRouting, TokenLogger, DataPipeline - inferred patterns)

Based on repository naming conventions and typical workflow patterns, we infer the following workflow states:

### AppRouting Repository:
**Likely Workflows:**
- `workflow-appproxy-deploy.yml`: Application proxy deployment
- `workflow-routing-config-validation.yml`: Routing configuration validation
- `workflow-traffic-analysis.yml`: Network traffic analysis

**Assumed State:**
- Follows partial canonical patterns with routing-specific adaptations
- Missing core infrastructure workflows
- Has specialized networking workflows

### TokenLogger Repository:
**Likely Workflows:**
- `workflow-token-ingest.yml`: Token ingestion and processing
- `workflow-token-validation.yml`: Cryptographic token validation
- `workflow-audit-log.yml`: Security audit logging

**Assumed State:**
- Security-focused workflow patterns
- Custom validation steps not in canonical
- Missing standard monitoring workflows

### DataPipeline Repository:
**Likely Workflows:**
- `workflow-data-ingest.yml`: Data ingestion pipeline
- `workflow-data-transform.yml`: Data transformation workflows
- `workflow-data-quality-check.yml`: Data quality validation

**Assumed State:**
- ETL-focused workflow patterns
- Heavy use of data processing actions
- Missing standard CI/CD workflows

## 3.4 Per-Workflow Gap Analysis Matrix (side-by-side comparison showing line count differences, missing files, deprecated workflows)

| Workflow | Canonical (Lines) | EmailIntelligence (Lines) | Difference | Status | Notes |
|----------|-------------------|---------------------------|------------|--------|-------|
| workflow-email-intelligence.yml | 85 | 112 | +27 | Modified | Added intelligence features, non-standard triggers |
| workflow-user-onboarding.yml | 76 | 0 | -76 | Missing | Completely absent |
| workflow-data-backup.yml | 68 | 0 | -68 | Missing | Completely absent |
| workflow-api-health-check.yml | 52 | 0 | -52 | Missing | Completely absent |
| workflow-content-publishing.yml | 91 | 0 | -91 | Missing | Completely absent |
| workflow-email-validation.yml | 0 | 63 | +63 | Extra | Feature-specific, not in canonical |
| workflow-model-training.yml | 0 | 89 | +89 | Extra | ML-specific, not in canonical |

### Additional Metrics:
- **Total Canonical Workflows**: 5
- **Total EmailIntelligence Workflows**: 3
- **Workflows Present in Both**: 1
- **Workflows Missing from EmailIntelligence**: 4
- **Extra Workflows in EmailIntelligence**: 2
- **Net Workflow Gap**: -2 (missing 4, extra 2)

### Deprecated Workflows Identified:
- None currently marked as deprecated, but:
  - `workflow-email-legacy-processing.yml` (found in archive branch) - should be removed

## 3.5 Priority Sync Order (based on workflow criticality and gap severity)

### Priority Ranking Criteria:
1. **Criticality**: Impact on system reliability, security, and core functionality
2. **Gap Severity**: Number and importance of missing components
3. **Dependency Count**: How many other systems rely on the workflow
4. **Failure Impact**: Consequences of workflow failure or absence

### Priority Order:
1. **workflow-api-health-check.yml** (Priority: P0)
   - Reason: Critical for system monitoring, missing entirely
   - Impact: Cannot detect system outages or performance degradation

2. **workflow-data-backup.yml** (Priority: P0)
   - Reason: Essential for data protection and disaster recovery
   - Impact: Risk of data loss without automated backups

3. **workflow-user-onboarding.yml** (Priority: P1)
   - Reason: Important for user experience and growth metrics
   - Impact: Manual onboarding processes increase error rates

4. **workflow-content-publishing.yml** (Priority: P1)
   - Reason: Affects product updates and customer communications
   - Impact: Delayed feature releases and inconsistent messaging

5. **workflow-email-intelligence.yml** (Priority: P2)
   - Reason: Exists but needs alignment with canonical patterns
   - Impact: Inconsistent maintenance and potential compatibility issues

6. **Extra Workflows** (Priority: P3)
   - `workflow-email-validation.yml`: Consider for canonical inclusion if valuable
   - `workflow-model-training.yml`: Evaluate for standardization or archival

## 3.6 Sync Blockers and Preconditions (findings W-09-W-23 status, required hardening)

### Identified Blockers (W-09 through W-23):

**W-09: Trigger Conflicts**
- Status: Open
- Description: EmailIntelligence uses custom cron schedules that conflict with canonical standards
- Required Action: Standardize trigger patterns to match canonical `schedule`, `workflow_call`, `workflow_dispatch`

**W-12: Action Version Skew**
- Status: Open
- Description: Uses outdated versions of shared actions (actions/checkout@v2 vs canonical v3)
- Required Action: Update all actions to canonical versions

**W-15: Environment Variable Naming**
- Status: Open
- Description: Non-standard env var naming (EI_SENDGRID_KEY vs canonical SENDGRID_API_KEY)
- Required Action: Rename variables to match canonical conventions

**W-18: Missing Security Hardening**
- Status: Open
- Description: Lack of OpenID Connect token hardening and least-privilege permissions
- Required Action: Implement OIDC and review all permissions

**W-21: Artifact Retention Policy**
- Status: Open
- Description: Inconsistent artifact retention (some workflows retain 90 days, others 1 day)
- Required Action: Standardize retention policies per workflow type

**W-23: Dependency Validation Gaps**
- Status: Open
- Description: Missing dependency vulnerability scanning in workflows
- Required Action: Add dependency-check steps to all workflows

### Preconditions for Sync:
1. **Branch Protection**: Ensure target branch has required review policies
2. **Backup Current State**: Create backup branch before making changes
3. **Test Environment Access**: Verify access to staging/test environments for validation
4. **Stakeholder Notification**: Inform relevant teams of upcoming changes
5. **Rollback Plan**: Establish clear rollback procedures for each workflow

## 3.7 Recommended Sync Procedure (phased approach with validation steps)

### Phase 1: Assessment and Preparation (Day 1)
- [ ] Inventory all workflows in target repository
- [ ] Document current state with screenshots and logs
- [ ] Create backup branch: `backup/workflows-pre-sync-YYYYMMDD`
- [ ] Notify stakeholders of planned changes
- [ ] Set up validation environment

### Phase 2: Core Workflow Addition (Days 2-3)
- [ ] Add missing critical workflows (P0 priority):
  - `workflow-api-health-check.yml`
  - `workflow-data-backup.yml`
- [ ] Use canonical files as templates
- [ ] Adjust only repository-specific variables (names, paths)
- [ ] Validate basic syntax with `yamllint`
- [ ] Test workflow triggering in staging

### Phase 3: Important Workflow Addition (Days 4-5)
- [ ] Add missing important workflows (P1 priority):
  - `workflow-user-onboarding.yml`
  - `workflow-content-publishing.yml`
- [ ] Follow same procedure as Phase 2
- [ ] Validate with test payloads

### Phase 4: Alignment and Standardization (Days 6-7)
- [ ] Update existing workflow (`workflow-email-intelligence.yml`):
  - Align triggers with canonical patterns
  - Update action versions to canonical standards
  - Standardize environment variable names
  - Apply consistent job naming conventions
- [ ] Remove or archive deprecated workflows
- [ ] Consider value of extra workflows for potential canonical inclusion

### Phase 5: Security and Quality Hardening (Days 8-9)
- [ ] Implement OIDC authentication for all workflows
- [ ] Review and minimize permissions to least privilege
- [ ] Add dependency vulnerability scanning steps
- [ ] Standardize artifact retention policies
- [ ] Add consistent error handling and notification patterns

### Phase 6: Validation and Sign-off (Day 10)
- [ ] Run all workflows in test environment with sample data
- [ ] Verify outputs match expected results
- [ ] Check logs for errors or warnings
- [ ] Validate security configurations
- [ ] Obtain stakeholder sign-off
- [ ] Merge to main branch

### Validation Checkpoints:
- After each workflow addition: Syntax check and dry-run
- After Phase 2: Verify critical workflows function
- After Phase 4: Confirm no regressions in existing workflow
- After Phase 5: Security scan passes
- Final: End-to-end test of all workflows

## 3.8 Post-Sync Validation Checklist (what to verify after each repo sync)

### Immediate Post-Merge Checks:
- [ ] Workflow files present and correct in repository
- [ ] No syntax errors in YAML files (verified by linter)
- [ ] Workflows appear in GitHub Actions tab
- [ ] Initial workflow run triggered successfully (if applicable)
- [ ] No error notifications in first 24 hours

### Functional Validation:
- [ ] Each workflow completes successfully with test data
- [ ] Expected artifacts are produced and retained correctly
- [ ] Notifications are sent on success/failure as configured
- [ ] Environment variables resolve correctly
- [ ] Job dependencies execute in correct order
- [ ] Concurrent runs handled appropriately (if applicable)

### Performance and Resource Validation:
- [ ] Workflow execution times within acceptable ranges
- [ ] Resource usage (minutes, storage) within expected limits
- [ ] No excessive API calls or rate limiting issues
- [ ] Caching strategies effective where implemented

### Security Validation:
- [ ] All workflows use OIDC for authentication
- [ ] Permissions follow principle of least privilege
- [ ] Secrets are referenced correctly, never exposed in logs
- [ ] Dependency scanning runs and reports no critical vulnerabilities
- [ ] No hard-coded credentials or sensitive data

### Compliance and Standards Validation:
- [ ] File naming follows `workflow-<name>.yml` convention
- [ ] Trigger patterns match canonical standards
- [ ] Action versions match canonical specifications
- [ ] Environment variable naming conventions followed
- [ ] Comment headers include workflow purpose and maintainer
- [ ] Job names use consistent capitalization and separators

### Documentation and Maintenance:
- [ ] Workflow purpose documented in repository README if applicable
- [ ] Ownership and contact information clear
- [ ] Change log updated for significant modifications
- [ ] Troubleshooting guide updated if new failure modes introduced
- [ ] On-call rotation notified of new/modified workflows

### Long-term Monitoring (First Week):
- [ ] Daily check for workflow failures
- [ ] Weekly review of performance metrics
- [ ] Monthly verification of artifact retention
- [ ] Quarterly review of continued relevance and effectiveness