# Session Tracking Data Retention Guidance

## Recommended Retention Policies

- **Active Sessions**: Keep session files for 30-90 days for active debugging and monitoring.
- **Archive Threshold**: Sessions older than 90 days should be archived to reduce storage overhead while maintaining accessibility.
- **Forensics Data**: Analyzed session data (forensics) provides long-term preservation and is retained indefinitely.

## Archival Process

The `archive_old_sessions.py` script automates the archival process:

1. Scans the `session_tracking/` directory (including subdirectories) for JSON session files.
2. For each file, checks the timestamp (using `last_update`, `updateTime`, or `createTime` fields) to determine its age.
3. Identifies files older than the specified threshold (default 90 days).
4. With `--dry-run`, lists files that would be archived without making changes.
5. Without `--dry-run`, moves old files to an archive directory structured as `session_tracking/archive/YYYY/MM/`.
6. Updates `SUMMARY.json` to reflect archived status or removes entries for archived files.
7. Creates a README in the archive directory explaining the archival policy.

## Accessing Archived Session Data

Archived session files are stored in:
```
session_tracking/archive/YYYY/MM/
```
Where `YYYY` is the year and `MM` is the month of the session's last update.

To access archived data:
- Navigate to the appropriate year/month directory.
- Session files retain their original names and JSON structure.
- The `SUMMARY.json` in the archive directory provides an index of archived sessions.

## Forensics Data Preservation

Forensics data (analyzed session results) is preserved separately and provides long-term retention of analyzed sessions. This data is not subject to the same archival policy as raw session files and is maintained for investigative and compliance purposes.

## Script Usage

```bash
# Dry run to see what would be archived
python archive_old_sessions.py --dry-run

# Archive old sessions (default 90 days)
python archive_old_sessions.py

# Specify a different threshold (e.g., 30 days)
python archive_old_sessions.py --days 30

# Restore archived sessions (bonus feature)
python archive_old_sessions.py --restore --archive-date 2024/01
```