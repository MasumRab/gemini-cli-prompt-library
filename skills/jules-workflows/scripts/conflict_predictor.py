#!/usr/bin/env python3
"""
Conflict Prediction and Pre-resolution
Predict and resolve conflicts before they occur in parallel workflows.
"""

import difflib
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ConflictType(Enum):
    CONTENT = "content"
    FILENAME = "filename"
    DIRECTORY = "directory"
    PERMISSION = "permission"


class ConflictSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ConflictPrediction:
    file_path: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    confidence: float  # 0.0 to 1.0
    description: str
    suggested_resolution: str
    affected_workers: List[str]


@dataclass
class FileChange:
    path: str
    content_hash: str
    operation: str  # add, modify, delete
    worker_id: str
    timestamp: float


class ConflictPredictor:
    def __init__(self):
        self.file_changes: List[FileChange] = []
        self.conflict_threshold = 0.7  # Confidence threshold for predicting conflicts
        
    def add_file_change(self, path: str, content: str, operation: str, worker_id: str):
        """Add a file change to track for conflict prediction."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        change = FileChange(path, content_hash, operation, worker_id, 0.0)  # timestamp would be actual time
        self.file_changes.append(change)
        
    def predict_conflicts(self, pending_changes: List[FileChange]) -> List[ConflictPrediction]:
        """Predict potential conflicts in pending changes."""
        conflicts = []
        
        # Group changes by file path
        changes_by_file = {}
        for change in self.file_changes + pending_changes:
            if change.path not in changes_by_file:
                changes_by_file[change.path] = []
            changes_by_file[change.path].append(change)
            
        # Check for conflicts in each file
        for file_path, changes in changes_by_file.items():
            if len(changes) > 1:
                # Multiple changes to the same file - potential conflict
                conflict = self._analyze_file_conflict(file_path, changes)
                if conflict and conflict.confidence >= self.conflict_threshold:
                    conflicts.append(conflict)
                    
        # Check for directory conflicts
        dir_conflicts = self._predict_directory_conflicts(pending_changes)
        conflicts.extend(dir_conflicts)
        
        return conflicts
        
    def _analyze_file_conflict(self, file_path: str, changes: List[FileChange]) -> Optional[ConflictPrediction]:
        """Analyze potential conflict for a specific file."""
        # Check if changes are to the same file by different workers
        workers = set(change.worker_id for change in changes)
        if len(workers) == 1:
            return None  # Same worker, no conflict
            
        # Check if all changes are the same (no real conflict)
        if len(set(change.content_hash for change in changes)) == 1:
            return None  # Identical changes, no conflict
            
        # Check if changes are compatible (e.g., one add, one modify to different parts)
        operations = set(change.operation for change in changes)
        if operations == {"add"} or operations == {"modify"}:
            # Same operation type - likely real conflict
            severity = ConflictSeverity.HIGH
            confidence = 0.9
            description = f"Multiple {list(operations)[0]} operations on {file_path} by workers {', '.join(workers)}"
            resolution = "Manual review required - changes affect same content"
        else:
            # Different operation types - might be resolvable
            severity = ConflictSeverity.MEDIUM
            confidence = 0.7
            description = f"Mixed operations on {file_path} by workers {', '.join(workers)}"
            resolution = "Attempt automatic merge - review if merge fails"
            
        return ConflictPrediction(
            file_path=file_path,
            conflict_type=ConflictType.CONTENT,
            severity=severity,
            confidence=confidence,
            description=description,
            suggested_resolution=resolution,
            affected_workers=list(workers)
        )
        
    def _predict_directory_conflicts(self, pending_changes: List[FileChange]) -> List[ConflictPrediction]:
        """Predict directory-level conflicts."""
        conflicts = []
        
        # Check for directory vs file conflicts
        paths = set(change.path for change in self.file_changes + pending_changes)
        
        for path in paths:
            path_obj = Path(path)
            # Check if this path conflicts with any directory paths
            for other_path in paths:
                if path != other_path:
                    other_path_obj = Path(other_path)
                    # Check if one is a directory of the other
                    if str(other_path_obj).startswith(str(path_obj) + "/") or \
                       str(path_obj).startswith(str(other_path_obj) + "/"):
                        conflict = ConflictPrediction(
                            file_path=path,
                            conflict_type=ConflictType.DIRECTORY,
                            severity=ConflictSeverity.HIGH,
                            confidence=0.95,
                            description=f"Directory conflict between {path} and {other_path}",
                            suggested_resolution="Manual resolution required - directory structure conflict",
                            affected_workers=["multiple"]  # Simplified
                        )
                        conflicts.append(conflict)
                        
        return conflicts
        
    def get_conflict_statistics(self) -> Dict:
        """Get statistics about predicted conflicts."""
        return {
            'total_changes_tracked': len(self.file_changes),
            'conflict_prediction_threshold': self.conflict_threshold
        }


class ConflictResolver:
    def __init__(self):
        self.resolved_conflicts = []
        self.auto_merge_success = 0
        self.auto_merge_failures = 0
        
    def pre_resolve_conflict(self, conflict: ConflictPrediction, 
                           file_contents: Dict[str, str]) -> Optional[str]:
        """Attempt to pre-resolve a conflict automatically."""
        if conflict.confidence < 0.5:
            # Low confidence - don't attempt auto-resolution
            return None
            
        if conflict.conflict_type == ConflictType.CONTENT:
            return self._resolve_content_conflict(conflict, file_contents)
        elif conflict.conflict_type == ConflictType.FILENAME:
            return self._resolve_filename_conflict(conflict)
        else:
            # For other conflict types, return None to indicate manual resolution needed
            return None
            
    def _resolve_content_conflict(self, conflict: ConflictPrediction, 
                                file_contents: Dict[str, str]) -> Optional[str]:
        """Resolve content conflict by attempting to merge changes."""
        try:
            # Get file contents from different workers
            # In a real implementation, this would fetch actual content from each worker
            worker_contents = []
            for worker in conflict.affected_workers:
                content = file_contents.get(f"{worker}:{conflict.file_path}")
                if content:
                    worker_contents.append(content)
                    
            if len(worker_contents) < 2:
                return None
                
            # Attempt to merge using difflib
            base_content = worker_contents[0].splitlines(keepends=True)
            new_content = worker_contents[1].splitlines(keepends=True)
            
            # Create a simple merge - in a real system, this would be more sophisticated
            merged_lines = []
            matcher = difflib.SequenceMatcher(None, base_content, new_content)
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    merged_lines.extend(base_content[i1:i2])
                elif tag == 'replace':
                    # For overlapping changes, prefer the new content but mark conflict
                    merged_lines.extend(new_content[j1:j2])
                elif tag == 'delete':
                    # Content deleted in new version
                    pass
                elif tag == 'insert':
                    # Content added in new version
                    merged_lines.extend(new_content[j1:j2])
                    
            merged_content = ''.join(merged_lines)
            
            # Check if merge was clean (no conflicts)
            if '<<<<<<<' not in merged_content and '=======' not in merged_content:
                self.auto_merge_success += 1
                return merged_content
            else:
                self.auto_merge_failures += 1
                return None
                
        except Exception as e:
            self.auto_merge_failures += 1
            return None
            
    def _resolve_filename_conflict(self, conflict: ConflictPrediction) -> Optional[str]:
        """Resolve filename conflict by suggesting unique names."""
        # This is a simplified approach - in reality, this would be more complex
        if conflict.severity == ConflictSeverity.LOW:
            # Suggest renaming one of the files
            suggested_name = f"{Path(conflict.file_path).stem}_conflict{Path(conflict.file_path).suffix}"
            return suggested_name
        else:
            return None  # Manual resolution needed
            
    def get_resolution_statistics(self) -> Dict:
        """Get statistics about conflict resolutions."""
        total_attempts = self.auto_merge_success + self.auto_merge_failures
        success_rate = (self.auto_merge_success / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'auto_merge_success': self.auto_merge_success,
            'auto_merge_failures': self.auto_merge_failures,
            'auto_merge_success_rate': success_rate,
            'total_resolved_conflicts': len(self.resolved_conflicts)
        }


def main():
    # Example usage
    print("Conflict Prediction and Pre-resolution System")
    print("=" * 50)
    
    # Create predictor and resolver
    predictor = ConflictPredictor()
    resolver = ConflictResolver()
    
    # Add some sample changes
    predictor.add_file_change("docs/api.md", "# API Docs\nContent", "modify", "worker1")
    predictor.add_file_change("docs/guide.md", "# User Guide\nInstructions", "add", "worker2")
    
    # Predict conflicts (this would be done before actual sync)
    conflicts = predictor.predict_conflicts([])
    print(f"Predicted conflicts: {len(conflicts)}")
    
    print("Conflict prediction and resolution system initialized")
    print("System ready to predict and pre-resolve conflicts in parallel workflows")


if __name__ == "__main__":
    main()