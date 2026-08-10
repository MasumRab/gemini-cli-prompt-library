#!/usr/bin/env python3
"""
Graphite Agent Zip Manager

Manages extraction, validation, and integration of zip-based Graphite agent artifacts.
Integrated with V8 implementation for complete agent deployment and verification.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class ZipManager:
    """Manages Graphite agent zip files and their integration with V8 implementation."""
    
    def __init__(self, base_dir: Path = None):
        """Initialize zip manager with base directory."""
        self.base_dir = base_dir or Path('.').resolve()
        self.agent_dir = self.base_dir / '.graphite-agent'
        self.zips_dir = self.agent_dir / 'zips'
        self.outputs_dir = self.agent_dir / 'outputs'
        self.tools_dir = self.agent_dir / 'tools'
        
        # Ensure directories exist
        self.zips_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def find_zip_files(self, pattern: str = '*.zip') -> List[Path]:
        """Find all zip files matching pattern in known locations."""
        zip_files = []
        seen_names = set()
        
        # Check local zips directory
        if self.zips_dir.exists():
            for zip_file in self.zips_dir.glob(pattern):
                if zip_file.name not in seen_names:
                    zip_files.append(zip_file)
                    seen_names.add(zip_file.name)
        
        # Check graphite-zips directory
        graphite_zips = self.base_dir / 'graphite-zips'
        if graphite_zips.exists():
            for zip_file in graphite_zips.glob(pattern):
                if zip_file.name not in seen_names:
                    zip_files.append(zip_file)
                    seen_names.add(zip_file.name)
        
        # Check current directory
        for zip_file in self.base_dir.glob(pattern):
            if zip_file.name not in seen_names:
                zip_files.append(zip_file)
                seen_names.add(zip_file.name)
        
        return sorted(zip_files)
    
    def get_zip_info(self, zip_path: Path) -> Dict[str, Any]:
        """Get information about a zip file."""
        info = {
            'path': str(zip_path),
            'name': zip_path.name,
            'size': zip_path.stat().st_size,
            'modified': datetime.fromtimestamp(zip_path.stat().st_mtime).isoformat(),
            'contents': []
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                infolist = zf.infolist()
                info['contents'] = [
                    {
                        'name': file_info.filename,
                        'size': file_info.file_size,
                        'is_dir': file_info.filename.endswith('/'),
                        'date_time': file_info.date_time
                    }
                    for file_info in infolist
                ]
                info['valid'] = True
                info['file_count'] = len(infolist)
        except Exception as e:
            info['valid'] = False
            info['error'] = str(e)
        
        return info
    
    def extract_zip(self, zip_path: Path, target_dir: Path = None, overwrite: bool = False) -> Tuple[bool, str]:
        """Extract a zip file to target directory."""
        target_dir = target_dir or self.agent_dir
        target_dir = target_dir.resolve()
        
        try:
            if target_dir.exists() and not overwrite:
                return False, f"Target directory {target_dir} already exists"
            
            # Create temp directory first
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract to temp
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(temp_path)
                
                # Move contents to target
                for item in temp_path.iterdir():
                    target_item = target_dir / item.name
                    if target_item.exists() and not overwrite:
                        continue
                    if item.is_dir():
                        shutil.copytree(item, target_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, target_item)
            
            return True, f"Extracted {zip_path.name} to {target_dir}"
            
        except Exception as e:
            return False, f"Failed to extract {zip_path.name}: {str(e)}"
    
    def validate_zip_contents(self, zip_path: Path, required_files: List[str] = None) -> Tuple[bool, Dict]:
        """Validate that a zip file contains required files."""
        required_files = required_files or [
            '.graphite-agent/main.py',
            '.graphite-agent/tools/semantic_inventory.py',
            '.graphite-agent/tools/ast_analyse.py',
            '.graphite-agent/tools/symbol_graph.py',
            '.graphite-agent/tools/reference_graph.py'
        ]
        
        result = {
            'zip': zip_path.name,
            'required_files': {},
            'missing_files': [],
            'extra_files': [],
            'valid': False
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                contents = {info.filename for info in zf.infolist()}
                
                for req_file in required_files:
                    found = any(req_file in name for name in contents)
                    result['required_files'][req_file] = found
                    if not found:
                        result['missing_files'].append(req_file)
                
                # Check for extra files not in standard locations
                standard_paths = ['.graphite-agent/', 'README.md', 'TEST_REPORT.md', 'KNOWN_LIMITATIONS.md']
                extra_files = [name for name in contents if not any(name.startswith(path) for path in standard_paths)]
                result['extra_files'] = extra_files[:10]  # Limit to first 10
                
                result['valid'] = len(result['missing_files']) == 0
                
        except Exception as e:
            result['error'] = str(e)
        
        return result['valid'], result
    
    def find_v8_zips(self) -> List[Path]:
        """Find all V8-related zip files."""
        all_zips = self.find_zip_files()
        v8_zips = [z for z in all_zips if 'v8' in z.name.lower()]
        return sorted(v8_zips)
    
    def find_latest_v8_zip(self) -> Optional[Path]:
        """Find the most recent V8 zip file."""
        v8_zips = self.find_v8_zips()
        if not v8_zips:
            return None
        
        # Sort by modification time, newest first
        v8_zips.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return v8_zips[0]
    
    def extract_and_integrate_v8(self, zip_path: Path = None, clean_extract: bool = False) -> Dict[str, Any]:
        """Extract V8 zip and integrate with existing implementation."""
        zip_path = zip_path or self.find_latest_v8_zip()
        if not zip_path:
            return {'success': False, 'error': 'No V8 zip files found'}
        
        result = {
            'zip': str(zip_path),
            'actions': [],
            'files_extracted': 0,
            'files_overwritten': 0,
            'files_merged': 0,
            'success': False
        }
        
        try:
            # Validate zip first
            valid, validation = self.validate_zip_contents(zip_path)
            if not valid:
                result['validation'] = validation
                result['error'] = f"Zip validation failed: {validation.get('missing_files', [])}"
                return result
            
            # Create extraction target
            extract_dir = self.agent_dir / 'v8_temp_extract'
            if clean_extract and extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract
            success, message = self.extract_zip(zip_path, extract_dir, overwrite=True)
            if not success:
                result['error'] = message
                return result
            
            result['actions'].append(message)
            
            # Count extracted files
            extracted_count = sum(1 for _ in extract_dir.rglob('*') if _.is_file())
            result['files_extracted'] = extracted_count
            
            # Integrate with existing tools
            tools_extracted = list((extract_dir / '.graphite-agent' / 'tools').rglob('*.py')) if (extract_dir / '.graphite-agent' / 'tools').exists() else []
            
            for tool_path in tools_extracted:
                relative_path = tool_path.relative_to(extract_dir / '.graphite-agent')
                target_path = self.tools_dir / relative_path
                
                if target_path.exists():
                    # Merge: backup existing and use new
                    backup_path = target_path.with_suffix('.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
                    shutil.copy2(target_path, backup_path)
                    result['files_overwritten'] += 1
                    result['actions'].append(f"Overwrote {relative_path} (backup created)")
                else:
                    result['files_merged'] += 1
                    result['actions'].append(f"Added {relative_path}")
                
                # Copy to target
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tool_path, target_path)
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        finally:
            # Cleanup temp directory
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
        
        return result
    
    def create_zip_from_current(self, name: str = 'graphite_agent_current.zip', 
                               include_outputs: bool = True) -> Tuple[bool, str]:
        """Create a zip file from current Graphite agent state."""
        zip_path = self.zips_dir / name
        
        try:
            included_files = []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add main agent files
                if self.agent_dir.exists():
                    for file_path in self.agent_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(self.agent_dir)
                            zf.write(file_path, arcname)
                            included_files.append(str(arcname))
                
                # Add outputs if requested
                if include_outputs and self.outputs_dir.exists():
                    for file_path in self.outputs_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = 'outputs/' + file_path.relative_to(self.outputs_dir).as_posix()
                            zf.write(file_path, arcname)
                            included_files.append(arcname)
            
            return True, f"Created {zip_path} with {len(included_files)} files"
            
        except Exception as e:
            return False, f"Failed to create zip: {str(e)}"
    
    def list_all_zips_with_info(self) -> List[Dict]:
        """List all zip files with their information."""
        zip_files = self.find_zip_files()
        return [self.get_zip_info(zip_file) for zip_file in zip_files]


def main():
    """Main entry point for zip manager CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Graphite Agent Zip Manager')
    parser.add_argument('--list', action='store_true', help='List all zip files')
    parser.add_argument('--extract', type=str, help='Extract specific zip file')
    parser.add_argument('--validate', type=str, help='Validate specific zip file')
    parser.add_argument('--find-v8', action='store_true', help='Find V8 zip files')
    parser.add_argument('--integrate-v8', action='store_true', help='Integrate latest V8 zip')
    parser.add_argument('--create-zip', type=str, help='Create zip from current state')
    parser.add_argument('--clean', action='store_true', help='Clean temporary files')
    
    args = parser.parse_args()
    
    manager = ZipManager()
    
    try:
        if args.list:
            zips = manager.list_all_zips_with_info()
            print(f"Found {len(zips)} zip files:")
            for zip_info in zips:
                status = "✅" if zip_info.get('valid', False) else "❌"
                print(f"  {status} {zip_info['name']} ({zip_info['size']} bytes, {zip_info.get('modified', 'unknown')})")
                if 'contents' in zip_info:
                    print(f"      Contents: {len(zip_info['contents'])} files")
        
        elif args.extract:
            zip_path = Path(args.extract)
            if not zip_path.exists():
                # Try to find in known locations
                found_zips = manager.find_zip_files(f'*{args.extract}*')
                if found_zips:
                    zip_path = found_zips[0]
                else:
                    print(f"❌ Zip file not found: {args.extract}")
                    return 1
            
            success, message = manager.extract_zip(zip_path)
            print(f"{'✅' if success else '❌'} {message}")
        
        elif args.validate:
            zip_path = Path(args.validate)
            if not zip_path.exists():
                found_zips = manager.find_zip_files(f'*{args.validate}*')
                if found_zips:
                    zip_path = found_zips[0]
                else:
                    print(f"❌ Zip file not found: {args.validate}")
                    return 1
            
            valid, result = manager.validate_zip_contents(zip_path)
            print(f"{'✅ Valid' if valid else '❌ Invalid'}: {zip_path.name}")
            if 'missing_files' in result and result['missing_files']:
                print(f"   Missing files: {result['missing_files']}")
        
        elif args.find_v8:
            v8_zips = manager.find_v8_zips()
            print(f"Found {len(v8_zips)} V8 zip files:")
            for zip_path in v8_zips:
                print(f"  - {zip_path.name} ({zip_path.stat().st_size} bytes)")
        
        elif args.integrate_v8:
            result = manager.extract_and_integrate_v8()
            print(f"{'✅ Success' if result['success'] else '❌ Failed'}: V8 Integration")
            if 'actions' in result:
                for action in result['actions']:
                    print(f"   {action}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        elif args.create_zip:
            success, message = manager.create_zip_from_current(args.create_zip)
            print(f"{'✅' if success else '❌'} {message}")
        
        else:
            # Default: show summary
            print("Graphite Agent Zip Manager")
            print("=" * 40)
            
            zips = manager.list_all_zips_with_info()
            v8_zips = manager.find_v8_zips()
            latest_v8 = manager.find_latest_v8_zip()
            
            print(f"Total zip files: {len(zips)}")
            print(f"V8 zip files: {len(v8_zips)}")
            print(f"Latest V8 zip: {latest_v8.name if latest_v8 else 'None'}")
            
            print("\nUse --help for available commands")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())


# For direct import usage
ZipManagerClass = ZipManager