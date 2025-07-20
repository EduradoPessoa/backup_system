"""
Restore Manager for Desktop Backup Application
Handles restoration of files from compressed backups.
"""

import os
import zipfile
import tarfile
import shutil
from pathlib import Path
from datetime import datetime

from utils import ensure_directory_exists

class RestoreManager:
    def __init__(self):
        pass
    
    def get_backup_contents(self, backup_path):
        """
        Get the contents of a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            list: List of dictionaries containing file information
        """
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file not found: {backup_path}")
        
        try:
            if backup_path.endswith('.zip'):
                return self._get_zip_contents(backup_path)
            elif backup_path.endswith('.tar.gz'):
                return self._get_tar_contents(backup_path)
            else:
                raise Exception(f"Unsupported backup format: {backup_path}")
                
        except Exception as e:
            raise Exception(f"Failed to read backup contents: {str(e)}")
    
    def _get_zip_contents(self, backup_path):
        """Get contents of ZIP backup."""
        contents = []
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            for info in zipf.infolist():
                if not info.is_dir():  # Skip directories
                    contents.append({
                        'name': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                        'modified': datetime(*info.date_time),
                        'path': info.filename
                    })
        
        return sorted(contents, key=lambda x: x['name'])
    
    def _get_tar_contents(self, backup_path):
        """Get contents of TAR.GZ backup."""
        contents = []
        
        with tarfile.open(backup_path, 'r:gz') as tarf:
            for member in tarf.getmembers():
                if member.isfile():  # Skip directories
                    contents.append({
                        'name': member.name,
                        'size': member.size,
                        'compressed_size': member.size,  # TAR doesn't provide compressed size per file
                        'modified': datetime.fromtimestamp(member.mtime),
                        'path': member.name
                    })
        
        return sorted(contents, key=lambda x: x['name'])
    
    def restore_files(self, backup_path, file_names, destination_path, 
                     preserve_structure=True, overwrite_existing=False):
        """
        Restore specific files from backup.
        
        Args:
            backup_path: Path to the backup file
            file_names: List of file names to restore (can be empty for all files)
            destination_path: Destination directory for restored files
            preserve_structure: Whether to preserve directory structure
            overwrite_existing: Whether to overwrite existing files
            
        Returns:
            dict: Results of restore operation
        """
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file not found: {backup_path}")
        
        if not os.path.exists(destination_path):
            raise Exception(f"Destination path not found: {destination_path}")
        
        try:
            if backup_path.endswith('.zip'):
                return self._restore_from_zip(backup_path, file_names, destination_path, 
                                            preserve_structure, overwrite_existing)
            elif backup_path.endswith('.tar.gz'):
                return self._restore_from_tar(backup_path, file_names, destination_path, 
                                            preserve_structure, overwrite_existing)
            else:
                raise Exception(f"Unsupported backup format: {backup_path}")
                
        except Exception as e:
            raise Exception(f"Restore failed: {str(e)}")
    
    def _restore_from_zip(self, backup_path, file_names, destination_path, 
                         preserve_structure, overwrite_existing):
        """Restore files from ZIP backup."""
        restored_files = []
        skipped_files = []
        errors = []
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Get list of files to restore
            if not file_names:  # Restore all files
                files_to_restore = [info.filename for info in zipf.infolist() if not info.is_dir()]
            else:
                files_to_restore = file_names
            
            for file_name in files_to_restore:
                try:
                    # Check if file exists in backup
                    if file_name not in zipf.namelist():
                        errors.append(f"File not found in backup: {file_name}")
                        continue
                    
                    # Determine destination file path
                    if preserve_structure:
                        dest_file_path = os.path.join(destination_path, file_name)
                    else:
                        dest_file_path = os.path.join(destination_path, os.path.basename(file_name))
                    
                    # Check if file already exists
                    if os.path.exists(dest_file_path) and not overwrite_existing:
                        skipped_files.append(f"File already exists: {dest_file_path}")
                        continue
                    
                    # Ensure destination directory exists
                    dest_dir = os.path.dirname(dest_file_path)
                    ensure_directory_exists(dest_dir)
                    
                    # Extract file
                    with zipf.open(file_name) as source, open(dest_file_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    restored_files.append(dest_file_path)
                    
                except Exception as e:
                    errors.append(f"Error restoring {file_name}: {str(e)}")
        
        return {
            'restored': restored_files,
            'skipped': skipped_files,
            'errors': errors,
            'total_restored': len(restored_files)
        }
    
    def _restore_from_tar(self, backup_path, file_names, destination_path, 
                         preserve_structure, overwrite_existing):
        """Restore files from TAR.GZ backup."""
        restored_files = []
        skipped_files = []
        errors = []
        
        with tarfile.open(backup_path, 'r:gz') as tarf:
            # Get list of files to restore
            if not file_names:  # Restore all files
                files_to_restore = [member.name for member in tarf.getmembers() if member.isfile()]
            else:
                files_to_restore = file_names
            
            for file_name in files_to_restore:
                try:
                    # Check if file exists in backup
                    try:
                        member = tarf.getmember(file_name)
                    except KeyError:
                        errors.append(f"File not found in backup: {file_name}")
                        continue
                    
                    if not member.isfile():
                        continue
                    
                    # Determine destination file path
                    if preserve_structure:
                        dest_file_path = os.path.join(destination_path, file_name)
                    else:
                        dest_file_path = os.path.join(destination_path, os.path.basename(file_name))
                    
                    # Check if file already exists
                    if os.path.exists(dest_file_path) and not overwrite_existing:
                        skipped_files.append(f"File already exists: {dest_file_path}")
                        continue
                    
                    # Ensure destination directory exists
                    dest_dir = os.path.dirname(dest_file_path)
                    ensure_directory_exists(dest_dir)
                    
                    # Extract file
                    extracted_file = tarf.extractfile(member)
                    if extracted_file:
                        with extracted_file as source, open(dest_file_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                    
                    # Preserve file permissions
                    try:
                        os.chmod(dest_file_path, member.mode)
                    except:
                        pass  # Ignore permission errors
                    
                    restored_files.append(dest_file_path)
                    
                except Exception as e:
                    errors.append(f"Error restoring {file_name}: {str(e)}")
        
        return {
            'restored': restored_files,
            'skipped': skipped_files,
            'errors': errors,
            'total_restored': len(restored_files)
        }
    
    def restore_all_files(self, backup_path, destination_path, overwrite_existing=False):
        """
        Restore all files from backup to destination.
        
        Args:
            backup_path: Path to the backup file
            destination_path: Destination directory
            overwrite_existing: Whether to overwrite existing files
        """
        return self.restore_files(backup_path, [], destination_path, 
                                preserve_structure=True, 
                                overwrite_existing=overwrite_existing)
    
    def extract_single_file(self, backup_path, file_name, destination_path):
        """
        Extract a single file from backup.
        
        Args:
            backup_path: Path to the backup file
            file_name: Name of file to extract
            destination_path: Destination file path
        """
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file not found: {backup_path}")
        
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_path)
            ensure_directory_exists(dest_dir)
            
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    with zipf.open(file_name) as source, open(destination_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
            
            elif backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tarf:
                    member = tarf.getmember(file_name)
                    extracted_file = tarf.extractfile(member)
                    if extracted_file:
                        with extracted_file as source, open(destination_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            
            else:
                raise Exception(f"Unsupported backup format: {backup_path}")
                
        except Exception as e:
            raise Exception(f"Failed to extract file {file_name}: {str(e)}")
    
    def verify_restore(self, backup_path, restored_files):
        """
        Verify that restored files match the backup contents.
        
        Args:
            backup_path: Path to the backup file
            restored_files: List of restored file paths
            
        Returns:
            dict: Verification results
        """
        verification_results = {
            'verified': [],
            'mismatches': [],
            'missing': []
        }
        
        try:
            backup_contents = self.get_backup_contents(backup_path)
            backup_files = {item['name']: item for item in backup_contents}
            
            for restored_file in restored_files:
                file_name = os.path.basename(restored_file)
                
                # Find corresponding backup file
                backup_file = None
                for name, info in backup_files.items():
                    if os.path.basename(name) == file_name:
                        backup_file = info
                        break
                
                if not backup_file:
                    verification_results['missing'].append(restored_file)
                    continue
                
                # Check file size
                if os.path.exists(restored_file):
                    restored_size = os.path.getsize(restored_file)
                    if restored_size == backup_file['size']:
                        verification_results['verified'].append(restored_file)
                    else:
                        verification_results['mismatches'].append({
                            'file': restored_file,
                            'expected_size': backup_file['size'],
                            'actual_size': restored_size
                        })
                else:
                    verification_results['missing'].append(restored_file)
            
        except Exception as e:
            raise Exception(f"Verification failed: {str(e)}")
        
        return verification_results
