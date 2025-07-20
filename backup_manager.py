"""
Backup Manager for Desktop Backup Application
Handles the creation and management of compressed backups.
"""

import os
import zipfile
import tarfile
import json
from pathlib import Path
from datetime import datetime
import threading
import shutil

from catalog_manager import CatalogManager
from utils import get_file_size, calculate_directory_size

class BackupManager:
    def __init__(self):
        self.catalog_manager = CatalogManager()
        self.cancel_flag = threading.Event()
    
    def create_backup(self, source_folders, destination_path, compression_type="zip", 
                     include_subdirs=True, progress_callback=None):
        """
        Create a compressed backup of the specified folders.
        
        Args:
            source_folders: List of folder paths to backup
            destination_path: Destination directory for backup
            compression_type: 'zip' or 'tar.gz'
            include_subdirs: Whether to include subdirectories
            progress_callback: Function to call with progress updates
        
        Returns:
            str: Backup filename if successful, None if failed
        """
        try:
            self.cancel_flag.clear()
            
            # Generate backup name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            
            if compression_type == "zip":
                backup_filename = f"{backup_name}.zip"
            else:
                backup_filename = f"{backup_name}.tar.gz"
            
            backup_path = os.path.join(destination_path, backup_filename)
            
            # Calculate total size for progress tracking
            if progress_callback:
                progress_callback(0, 100, "Calculating backup size...")
            
            total_size = 0
            file_list = []
            
            for source_folder in source_folders:
                if self.cancel_flag.is_set():
                    return None
                
                folder_files = self._get_files_to_backup(source_folder, include_subdirs)
                file_list.extend(folder_files)
                
                for file_path in folder_files:
                    try:
                        total_size += get_file_size(file_path)
                    except (OSError, IOError):
                        continue
            
            if not file_list:
                raise Exception("No files found to backup")
            
            # Create backup
            if compression_type == "zip":
                success = self._create_zip_backup(backup_path, file_list, source_folders, 
                                                total_size, progress_callback)
            else:
                success = self._create_tar_backup(backup_path, file_list, source_folders, 
                                                total_size, progress_callback)
            
            if success and not self.cancel_flag.is_set():
                # Create catalog entry
                catalog_entry = {
                    'name': backup_name,
                    'filename': backup_filename,
                    'path': backup_path,
                    'date': datetime.now().isoformat(),
                    'size': get_file_size(backup_path),
                    'compression': compression_type,
                    'source_folders': source_folders,
                    'file_count': len(file_list),
                    'files': [{'name': f, 'size': get_file_size(f)} for f in file_list if os.path.exists(f)]
                }
                
                self.catalog_manager.add_catalog_entry(catalog_entry)
                
                if progress_callback:
                    progress_callback(100, 100, f"Backup completed: {backup_filename}")
                
                return backup_name
            else:
                # Cleanup failed backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                return None
                
        except Exception as e:
            # Cleanup on error
            if 'backup_path' in locals() and os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except:
                    pass
            raise Exception(f"Backup failed: {str(e)}")
    
    def _get_files_to_backup(self, source_folder, include_subdirs):
        """Get list of files to backup from source folder."""
        files = []
        
        if not os.path.exists(source_folder):
            return files
        
        try:
            if include_subdirs:
                for root, dirs, filenames in os.walk(source_folder):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            files.append(file_path)
            else:
                for item in os.listdir(source_folder):
                    item_path = os.path.join(source_folder, item)
                    if os.path.isfile(item_path):
                        files.append(item_path)
        except (OSError, IOError) as e:
            raise Exception(f"Error accessing folder {source_folder}: {str(e)}")
        
        return files
    
    def _create_zip_backup(self, backup_path, file_list, source_folders, total_size, progress_callback):
        """Create ZIP backup."""
        try:
            processed_size = 0
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for file_path in file_list:
                    if self.cancel_flag.is_set():
                        return False
                    
                    try:
                        # Calculate relative path for archive
                        arcname = self._get_archive_name(file_path, source_folders)
                        
                        # Add file to archive
                        zipf.write(file_path, arcname)
                        
                        # Update progress
                        file_size = get_file_size(file_path)
                        processed_size += file_size
                        
                        if progress_callback and total_size > 0:
                            progress = (processed_size / total_size) * 100
                            progress_callback(progress, 100, f"Backing up: {os.path.basename(file_path)}")
                    
                    except (OSError, IOError) as e:
                        # Skip files that can't be read
                        if progress_callback:
                            progress_callback(processed_size / total_size * 100, 100, 
                                            f"Skipped: {os.path.basename(file_path)} ({str(e)})")
                        continue
            
            return True
            
        except Exception as e:
            raise Exception(f"ZIP creation failed: {str(e)}")
    
    def _create_tar_backup(self, backup_path, file_list, source_folders, total_size, progress_callback):
        """Create TAR.GZ backup."""
        try:
            processed_size = 0
            
            with tarfile.open(backup_path, 'w:gz') as tarf:
                for file_path in file_list:
                    if self.cancel_flag.is_set():
                        return False
                    
                    try:
                        # Calculate relative path for archive
                        arcname = self._get_archive_name(file_path, source_folders)
                        
                        # Add file to archive
                        tarf.add(file_path, arcname=arcname, recursive=False)
                        
                        # Update progress
                        file_size = get_file_size(file_path)
                        processed_size += file_size
                        
                        if progress_callback and total_size > 0:
                            progress = (processed_size / total_size) * 100
                            progress_callback(progress, 100, f"Backing up: {os.path.basename(file_path)}")
                    
                    except (OSError, IOError) as e:
                        # Skip files that can't be read
                        if progress_callback:
                            progress_callback(processed_size / total_size * 100, 100, 
                                            f"Skipped: {os.path.basename(file_path)} ({str(e)})")
                        continue
            
            return True
            
        except Exception as e:
            raise Exception(f"TAR creation failed: {str(e)}")
    
    def _get_archive_name(self, file_path, source_folders):
        """Generate archive name for file maintaining folder structure."""
        # Find which source folder this file belongs to
        for source_folder in source_folders:
            if file_path.startswith(source_folder):
                # Get relative path from source folder
                rel_path = os.path.relpath(file_path, source_folder)
                # Prefix with source folder name to avoid conflicts
                folder_name = os.path.basename(source_folder.rstrip(os.sep))
                return os.path.join(folder_name, rel_path).replace(os.sep, '/')
        
        # Fallback: use just the filename
        return os.path.basename(file_path)
    
    def cancel_backup(self):
        """Cancel the current backup operation."""
        self.cancel_flag.set()
    
    def verify_backup(self, backup_path):
        """Verify the integrity of a backup file."""
        try:
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    bad_files = zipf.testzip()
                    return bad_files is None
            elif backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tarf:
                    # TAR files don't have a built-in test method
                    # We'll try to read the member list
                    members = tarf.getmembers()
                    return len(members) > 0
            else:
                return False
                
        except Exception:
            return False
