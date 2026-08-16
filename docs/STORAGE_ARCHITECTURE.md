# Jules Storage Architecture

This document describes the storage systems used in the Jules repository, detailing what each store contains, typical access patterns, data flow between systems, and retention policies.

## 1. Session Tracking Files (`/session_tracking/`)

### What it contains
Detailed prompt/response logs for each interaction session. Each file typically contains:
- User prompts
- Agent responses
- Timestamps
- Context metadata
- Error information and debugging details

### Typical access patterns and use cases
- Debugging agent behavior
- Auditing conversation history
- Training data collection for model improvement
- User support and issue investigation
- Access is primarily read-heavy, with occasional writes during active sessions

### How data flows into it
Data is written directly by the session management system during each agent interaction. Files are typically created per session or rotated based on size/time thresholds.

### Retention/persistence characteristics
- Medium-term retention (typically 30-90 days)
- Files may be archived or deleted after retention period
- Not backed up as aggressively as critical databases due to volume
- May be subject to GDPR/data deletion requests

### How it relates to other stores
- Feeds summarized data into the SQLite database (`store.db`) for metadata and activity summaries
- May be referenced by forensics analysis for detailed incident investigation
- Activity logs may correlate with session tracking files via session IDs

## 2. SQLite Database (`~/.jules/store.db`)

### What it contains
Session metadata and activity summaries with Full-Text Search (FTS) capabilities:
- Session identifiers and timestamps
- User and agent metadata
- Activity summaries and metrics
- FTS indexes for searching prompt/response content
- Configuration settings and preferences

### Typical access patterns and use cases
- Quick lookup of session metadata
- Searching conversation history via FTS
- Generating activity reports and dashboards
- Tracking user engagement and system usage
- Frequent read operations with periodic writes

### How data flows into it
Data flows from session tracking files through periodic summarization processes or direct logging during session events. The database is updated in real-time or near real-time as sessions progress.

### Retention/persistence characteristics
- Long-term retention (typically 1-2 years)
- Regular backups due to critical metadata nature
- Data may be aggregated or anonymized after extended periods
- FTS indexes are rebuilt periodically

### How it relates to other stores
- Receives summarized data from session tracking files
- Provides metadata that enriches forensics analysis
- Activity logs may reference session IDs stored here
- Sent responses log entries may be correlated via session IDs

## 3. Forensics Data (`/docs/forensics/migrated_forensics_data.json`)

### What it contains
Standardized longitudinal analysis data for forensic investigations:
- Normalized session data across time periods
- Anomaly detection results
- Security incident markers
- Performance baselines and deviations
- User behavior patterns over extended periods

### Typical access patterns and use cases
- Security audits and incident investigations
- Trend analysis and capacity planning
- Compliance reporting
- Machine learning model training for anomaly detection
- Primarily read-heavy analytical workloads

### How data flows into it
Data is aggregated from session tracking files, SQLite database, and activity logs through ETL (Extract, Transform, Load) processes. Standardization scripts convert raw data into the forensic format.

### Retention/persistence characteristics
- Very long-term retention (indefinite or legal hold)
- Treated as archival data
- Immutable once written (write-once-read-many)
- Regular integrity checks and backups
- May be subject to legal retention requirements

### How it relates to other stores
- Consumes data from all other stores (session tracking, SQLite, activity logs, sent responses)
- Provides a unified view for cross-store analysis
- Acts as a historical reference for current session analysis
- May feed back insights to improve other storage systems

## 4. Activity Logs (`/data/` and root `activities_*.json`)

### What it contains
Agent-specific operational metrics and logs:
- Agent execution times and resource usage
- Task queue metrics and throughput
- Error rates and failure patterns
- System health indicators
- Custom metrics per agent type

### Typical access patterns and use cases
- Real-time monitoring and alerting
- Performance tuning and optimization
- Capacity planning and scaling decisions
- Debugging agent-specific issues
- Operational dashboards (e.g., Grafana, Kibana)

### How data flows intoi
Data is written directly by agents during operation, typically using structured logging frameworks. Logs may be rotated based on size or time.

### Retention/persistence characteristics
- Short to medium-term retention (typically 7-30 days for detailed logs)
- Aggregated metrics may be retained longer
- Often shipped to centralized logging systems (ELK stack, etc.)
- Subject to log rotation and compression policies

### How it relates to other stores
- Provides operational context for session tracking data
- Metrics may be summarized into the SQLite database
- Correlates with forensics data for incident root cause analysis
- May trigger alerts that lead to session tracking reviews

## 5. Sent Responses Log (`/skills/jules-sessions/references/sent_responses.md`)

### What it contains
Record of operator interventions and manually sent responses:
- Operator-overridden responses
- Manual interventions during agent failures
- Training examples for corrective behavior
- Comments and rationale for interventions
- Timestamps and operator identification

### Typical access patterns and use cases
- Tracking human-in-the-loop corrections
- Improving agent training data
- Auditing override frequency and patterns
- Quality assurance and compliance checks
- Identifying common failure modes requiring intervention

### How data flows into it
Data is appended manually by operators when they intervene in agent sessions, or automatically when the system logs override events. Format is typically markdown for easy human readability.

### Retention/persistence characteristics
- Long-term retention (indefinite)
- Treated as training and audit material
- May be periodically reviewed and cleaned
- Backed up as part of critical documentation
- Subject to review for sensitive information

### How it relates to other stores
- References specific sessions from session tracking files
- May be correlated with SQLite database entries
- Used to adjust forensics analysis (removing outliers from intervention)
- Activity logs may show increased operator load correlating with entries