#!/usr/bin/env python3
"""
Script to migrate existing forensics data (Markdown and JSON files)
to the standardized JSON format defined in forensics_data_schema.json.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ForensicsDataMigrator:
    def __init__(self, forensics_dir: str):
        self.forensics_dir = forensics_dir
        self.schema_path = os.path.join(forensics_dir, "forensics_data_schema.json")
        self.output_path = os.path.join(forensics_dir, "migrated_forensics_data.json")

        # Initialize data structures according to schema
        self.migrated_data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "update_frequency": "per migration run",
                "analysis_thread": "",
                "version": "1.0.0",
                "total_sessions": 0,
                "total_prs": 0,
                "total_interventions": 0,
                "source_sessions_count": 0,
            },
            "sessions": [],
            "pull_requests": [],
            "interventions": [],
        }

        # Track seen entities to avoid duplicates
        self.session_ids_seen = set()
        self.pr_keys_seen = set()  # tuple of (number, repo)
        self.intervention_keys_seen = (
            set()
        )  # tuple of (session_id, intervention_type, created)

    def load_schema(self) -> Dict[str, Any]:
        """Load the forensics data schema."""
        try:
            with open(self.schema_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def validate_against_schema(self, data: Dict[str, Any]) -> bool:
        """Basic validation against schema (simplified)."""
        # In a full implementation, we would use jsonschema library
        # For now, we'll do basic structural validation
        required_top_level = ["metadata", "sessions", "pull_requests", "interventions"]
        for key in required_top_level:
            if key not in data:
                logger.error(f"Missing required top-level key: {key}")
                return False

        metadata_required = ["generated_at", "analysis_thread", "version"]
        for key in metadata_required:
            if key not in data["metadata"]:
                logger.error(f"Missing required metadata key: {key}")
                return False

        return True

    def extract_session_id_from_text(self, text: str) -> Optional[str]:
        """Extract session ID from various text formats."""
        # Look for patterns like session_id: "12345" or session_id: 12345
        patterns = [
            r'session_id["\']?\s*[:=]\s*["\']?(\d+)',
            r'"session_id"\s*:\s*"(\d+)"',
            r"session_id\s*:\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def extract_pr_info_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract PR information from text."""
        prs = []
        # Look for PR patterns like PR #123 or PR #123: title
        pr_pattern = r"PR\s+#(\d+)(?:\s*:|\s*-|\s+)?([^\n]*)"
        matches = re.findall(pr_pattern, text, re.IGNORECASE)

        for match in matches:
            pr_number = int(match[0])
            pr_title = match[1].strip()
            prs.append(
                {
                    "number": pr_number,
                    "title": pr_title if pr_title else f"PR #{pr_number}",
                }
            )

        return prs

    def process_intervention_e2e_ledger(self, filepath: str):
        """Process intervention_e2e_ledger JSON file."""
        logger.info(f"Processing intervention_e2e_ledger: {filepath}")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Extract metadata - preserve migration timestamp for generated_at and last_updated
            # Only overwrite analysis_thread from source data if available
            if "analysis_thread" in data:
                self.migrated_data["metadata"]["analysis_thread"] = data[
                    "analysis_thread"
                ]

            # Process entries as interventions
            if "entries" in data and isinstance(data["entries"], list):
                for entry in data["entries"]:
                    self._process_intervention_entry(entry)

        except Exception as e:
            logger.error(f"Error processing intervention_e2e_ledger: {e}")

    def _process_intervention_entry(self, entry: Dict[str, Any]):
        """Process a single intervention entry."""
        try:
            # Create intervention key for deduplication
            session_id = str(entry.get("session_id", ""))
            intervention_type = entry.get("intervention_type", "")
            created = entry.get("created", "")
            key = (session_id, intervention_type, created)

            if key in self.intervention_keys_seen:
                return
            self.intervention_keys_seen.add(key)

            # Map entry to intervention schema
            intervention = {
                "session_id": session_id,
                "repo": entry.get("repo", ""),
                "pr": entry.get("pr", None)
                if entry.get("pr") and entry.get("pr") != "no PR"
                else None,
                "title": entry.get("title", None),
                "created": entry.get("created", ""),
                "intervention_type": entry.get("intervention_type", ""),
                "intervention_intent": entry.get("intervention_intent", ""),
                "pre_state": entry.get("pre_state", ""),
                "immediate_post_state": entry.get("immediate_post_state", ""),
                "current_state": entry.get("current_state", ""),
                "current_updated": entry.get("current_updated", ""),
                "state_changed": entry.get("state_changed", False),
                "agent_produced_output": entry.get("agent_produced_output", False),
                "output_posted": entry.get("output_posted", False),
                "outcome_class": entry.get("outcome_class", ""),
                "evidence": entry.get("evidence", ""),
                "confidence": entry.get("confidence", "medium"),
                "new_activities": entry.get("new_activities"),
                "has_agent_messages": entry.get("has_agent_messages"),
                "agent_message_count": entry.get("agent_message_count"),
                "note": entry.get("note"),
                "pr_state": entry.get("pr_state"),
                "recovery_comments_posted": entry.get("recovery_comments_posted"),
                "has_duplicate": entry.get("has_duplicate"),
                "jules_bot_duplicate_count": entry.get("jules_bot_duplicate_count"),
                "post_intervention_comments": entry.get("post_intervention_comments"),
                "post_intervention_reviews": entry.get("post_intervention_reviews"),
                "post_intervention_commits": entry.get("post_intervention_commits"),
                "posted_to_correct_pr": entry.get("posted_to_correct_pr"),
                "formatting_valid": entry.get("formatting_valid"),
                "dedup_marker_present": entry.get("dedup_marker_present"),
                "detailed_analysis": entry.get("detailed_analysis"),
            }

            # Remove None values for cleaner output
            intervention = {k: v for k, v in intervention.items() if v is not None}

            self.migrated_data["interventions"].append(intervention)

        except Exception as e:
            logger.error(f"Error processing intervention entry: {e}")

    def process_session_pr_integrated(self, filepath: str):
        """Process session_pr_integrated JSON file."""
        logger.info(f"Processing session_pr_integrated: {filepath}")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                sessions = data
            elif isinstance(data, dict):
                sessions = data.get("sessions", [])
            else:
                sessions = []

            if not sessions:
                logger.warning("session_pr_integrated contains no sessions to process")
                return

            for session_data in sessions:
                self._process_session_entry(session_data)

        except Exception as e:
            logger.error(f"Error processing session_pr_integrated: {e}")

    def _process_session_entry(self, session_data: Dict[str, Any]):
        """Process a single session entry."""
        try:
            session_id = str(session_data.get("session_id", ""))
            if not session_id or session_id in self.session_ids_seen:
                return
            self.session_ids_seen.add(session_id)

            # Process session
            session = {
                "session_id": session_id,
                "session_state": session_data.get("session_state", "UNKNOWN"),
                "session_title": session_data.get("session_title", ""),
                "session_repo": session_data.get("session_repo", ""),
                "created_at": session_data.get("created_at", ""),
                "updated_at": session_data.get("updated_at", ""),
                "associated_prs": [],
                "timeline": [],
            }

            # Process PRs associated with this session
            if "prs" in session_data and isinstance(session_data["prs"], list):
                for pr_data in session_data["prs"]:
                    pr_number = pr_data.get("number")
                    pr_repo = pr_data.get("repo")
                    if pr_number is not None and pr_repo is not None:
                        pr_key = (pr_number, pr_repo)

                        # Add PR reference to session's associated_prs list (avoid duplicates)
                        pr_ref = {"number": pr_number, "repo": pr_repo}
                        if pr_ref not in session["associated_prs"]:
                            session["associated_prs"].append(pr_ref)

                        # Handle PR entry in pull_requests array
                        if pr_key not in self.pr_keys_seen:
                            # New PR: create entry and add to tracking set
                            self.pr_keys_seen.add(pr_key)

                            # Build PR entry
                            pr = {
                                "number": pr_number,
                                "repo": pr_repo,
                                "title": pr_data.get("title", ""),
                                "state": pr_data.get("state", "UNKNOWN"),
                                "head": pr_data.get("head", ""),
                                "base": pr_data.get("base", ""),
                                "created_at": pr_data.get("created", ""),
                                "updated_at": pr_data.get("updated", ""),
                                "merged_at": pr_data.get("merged"),
                                "closed_at": pr_data.get("closed"),
                                "url": pr_data.get("url", ""),
                                "comment_count": pr_data.get("comment_count", 0),
                                "review_count": pr_data.get("review_count", 0),
                                "commit_count": pr_data.get("commit_count", 0),
                                "associated_sessions": [
                                    session_id
                                ],  # Start with current session
                                "timeline": [],
                            }

                            # Process timeline entries if present
                            if "timeline" in pr_data and isinstance(
                                pr_data["timeline"], list
                            ):
                                for tl_entry in pr_data["timeline"]:
                                    timeline_entry = {
                                        "type": tl_entry.get("type", "comment"),
                                        "time": tl_entry.get("time", ""),
                                        "author": tl_entry.get("author", ""),
                                        "text": tl_entry.get("text", ""),
                                        "state": tl_entry.get("state"),
                                        "location": tl_entry.get("location"),
                                    }
                                    # Remove None values
                                    timeline_entry = {
                                        k: v
                                        for k, v in timeline_entry.items()
                                        if v is not None
                                    }
                                    pr["timeline"].append(timeline_entry)

                            self.migrated_data["pull_requests"].append(pr)
                        else:
                            # Existing PR: find it and update associated_sessions
                            for existing_pr in self.migrated_data["pull_requests"]:
                                if (
                                    existing_pr.get("number") == pr_number
                                    and existing_pr.get("repo") == pr_repo
                                ):
                                    # Avoid duplicate session references
                                    if (
                                        session_id
                                        not in existing_pr["associated_sessions"]
                                    ):
                                        existing_pr["associated_sessions"].append(
                                            session_id
                                        )
                                    break

            # Remove empty arrays if needed
            if not session["associated_prs"]:
                del session["associated_prs"]
            if not session["timeline"]:
                del session["timeline"]

            self.migrated_data["sessions"].append(session)

        except Exception as e:
            logger.error(f"Error processing session entry: {e}")

    def process_markdown_file(self, filepath: str):
        """Process a Markdown file to extract relevant information."""
        logger.info(f"Processing Markdown file: {filepath}")
        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Extract session IDs
            session_ids = re.findall(
                r'session[_\s]*id[:\s]*["\']?(\d+)', content, re.IGNORECASE
            )
            for session_id in session_ids:
                if session_id not in self.session_ids_seen:
                    self.session_ids_seen.add(session_id)
                    # Create a basic session entry
                    session = {
                        "session_id": session_id,
                        "session_state": "UNKNOWN",
                        "session_title": f"Session {session_id} (extracted from Markdown)",
                        "session_repo": "unknown",
                    }
                    self.migrated_data["sessions"].append(session)

            # Extract PR information
            pr_matches = re.findall(r"PR\s+#(\d+)", content, re.IGNORECASE)
            for pr_num_str in pr_matches:
                pr_num = int(pr_num_str)
                # We don't have repo info from markdown, so we'll skip adding to PRs for now
                # In a real implementation, we might infer repo from context

        except Exception as e:
            logger.error(f"Error processing Markdown file {filepath}: {e}")

    def process_json_file(self, filepath: str):
        """Process a generic JSON file."""
        logger.info(f"Processing JSON file: {filepath}")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Try to extract useful information based on filename
            filename = os.path.basename(filepath)

            if "session" in filename.lower() and "followup" in filename.lower():
                self._process_session_followup_data(data)
            elif "pr_migration" in filename.lower():
                self._process_pr_migration_data(data)
            elif "nonterminal" in filename.lower():
                self._process_nonterminal_triage_data(data)
            elif "scratch" in filepath:
                # Process scratch files if needed
                pass
            else:
                # Generic processing - look for session IDs and PR references
                self._extract_generic_info(data, filename)

        except Exception as e:
            logger.error(f"Error processing JSON file {filepath}: {e}")

    def _process_session_followup_data(self, data: Dict[str, Any]):
        """Process session followup tracker data."""
        # Implementation would depend on the structure of this file
        pass

    def _process_pr_migration_data(self, data: Dict[str, Any]):
        """Process PR migration plan data."""
        # Implementation would depend on the structure of this file
        pass

    def _process_nonterminal_triage_data(self, data: Dict[str, Any]):
        """Process nonterminal triage data."""
        # Implementation would depend on the structure of this file
        pass

    def _extract_generic_info(self, data: Any, filename: str):
        """Extract generic information from JSON data."""
        # Convert to string to search for patterns
        if isinstance(data, dict):
            text = json.dumps(data)
        elif isinstance(data, list):
            text = json.dumps(data)
        else:
            text = str(data)

        # Extract session IDs
        session_ids = re.findall(
            r'"?session_id"?\s*[:=]\s*["\']?(\d+)', text, re.IGNORECASE
        )
        for session_id in session_ids:
            if session_id not in self.session_ids_seen:
                self.session_ids_seen.add(session_id)
                session = {
                    "session_id": session_id,
                    "session_state": "UNKNOWN",
                    "session_title": f"Session {session_id} (extracted from {filename})",
                    "session_repo": "unknown",
                }
                self.migrated_data["sessions"].append(session)

    def run_migration(self):
        """Run the complete migration process."""
        logger.info("Starting forensics data migration...")

        # Process specific known files first
        specific_files = [
            (
                "intervention_e2e_ledger_2026-08-07.json",
                self.process_intervention_e2e_ledger,
            ),
            (
                "session_pr_integrated_2026-08-06.json",
                self.process_session_pr_integrated,
            ),
            ("SESSION_FOLLOWUP_TRACKER_2026-08-06.json", self.process_json_file),
            ("pr_migration_plan_2026-08-06.json", self.process_json_file),
            ("session_priority_batch_plan_2026-08-14.json", self.process_json_file),
            ("nonterminal_triage_2026-08-06.json", self.process_json_file),
        ]

        for filename, processor in specific_files:
            filepath = os.path.join(self.forensics_dir, filename)
            if os.path.exists(filepath):
                processor(filepath)
            else:
                logger.warning(f"File not found: {filepath}")

        # Process all JSON files in the directory
        json_pattern = os.path.join(self.forensics_dir, "*.json")
        import glob

        json_files = glob.glob(json_pattern)
        for filepath in json_files:
            filename = os.path.basename(filepath)
            # Skip already processed files and schema
            if (
                filename not in [f[0] for f in specific_files]
                and filename != "forensics_data_schema.json"
            ):
                self.process_json_file(filepath)

        # Process all Markdown files
        md_pattern = os.path.join(self.forensics_dir, "*.md")
        md_files = glob.glob(md_pattern)
        for filepath in md_files:
            self.process_markdown_file(filepath)

        # Process scratch directory if it exists
        scratch_dir = os.path.join(self.forensics_dir, "scratch")
        if os.path.exists(scratch_dir) and os.path.isdir(scratch_dir):
            logger.info(f"Processing scratch directory: {scratch_dir}")
            scratch_files = glob.glob(os.path.join(scratch_dir, "*"))
            for filepath in scratch_files:
                if os.path.isfile(filepath):
                    if filepath.endswith(".json"):
                        self.process_json_file(filepath)
                    elif filepath.endswith(".md"):
                        self.process_markdown_file(filepath)

        # Update metadata counts
        self.migrated_data["metadata"]["total_sessions"] = len(
            self.migrated_data["sessions"]
        )
        self.migrated_data["metadata"]["total_prs"] = len(
            self.migrated_data["pull_requests"]
        )
        self.migrated_data["metadata"]["total_interventions"] = len(
            self.migrated_data["interventions"]
        )
        # Add source sessions count (same as total_sessions for now)
        self.migrated_data["metadata"]["source_sessions_count"] = self.migrated_data[
            "metadata"
        ]["total_sessions"]

        logger.info(f"Migration complete. Processed:")
        logger.info(f"  - Sessions: {self.migrated_data['metadata']['total_sessions']}")
        logger.info(f"  - Pull Requests: {self.migrated_data['metadata']['total_prs']}")
        logger.info(
            f"  - Interventions: {self.migrated_data['metadata']['total_interventions']}"
        )

        # Validate against schema
        if self.validate_against_schema(self.migrated_data):
            logger.info("Data validates against schema")
        else:
            logger.warning("Data may not fully conform to schema")

        # Write output
        try:
            with open(self.output_path, "w") as f:
                json.dump(self.migrated_data, f, indent=2)
            logger.info(f"Migrated data written to: {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            raise


def show_schema_info(forensics_dir: str) -> int:
    """Show current schema version and migration history."""
    schema_path = os.path.join(forensics_dir, "forensics_data_schema.json")
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        return 1

    # Get metadata definition from definitions
    metadata_def = schema.get("definitions", {}).get("Metadata", {})

    # Get migrations from the migrations property
    migrations_prop = metadata_def.get("properties", {}).get("migrations", {})
    migrations = migrations_prop.get("default", [])

    # Determine current version from latest migration
    version = "unknown"
    if migrations:
        # Sort by version (simple semantic version sorting)
        try:
            sorted_migrations = sorted(
                migrations, key=lambda x: list(map(int, x["version"].split(".")))
            )
            version = sorted_migrations[-1]["version"]
        except:
            version = migrations[-1]["version"] if migrations else "unknown"

    print(f"Current schema version: {version}")
    print("\nMigration history:")
    if not migrations:
        print("  No migrations recorded.")
    else:
        for i, migration in enumerate(migrations, 1):
            ver = migration.get("version", "unknown")
            date = migration.get("date", "unknown")
            desc = migration.get("description", "No description")
            script = migration.get("script")
            script_str = f" (script: {script})" if script else ""
            print(f"  {i}. Version {ver} ({date}){script_str}")
            print(f"     {desc}")

    return 0


def main():
    """Main function to run the migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate forensics data to standardized schema"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show current schema version and migration history",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply migrations (not yet implemented)"
    )
    args = parser.parse_args()

    forensics_dir = "/home/masum/github/remote/jules/docs/forensics"

    if not os.path.exists(forensics_dir):
        logger.error(f"Forensics directory does not exist: {forensics_dir}")
        return 1

    if args.info:
        return show_schema_info(forensics_dir)

    migrator = ForensicsDataMigrator(forensics_dir)
    try:
        migrator.run_migration()
        return 0
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
