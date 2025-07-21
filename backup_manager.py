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
from utils import get_file_size, calculate_directory_size, format_size
from open_files_handler import OpenFilesHandler, create_backup_report
from user_manager import user_manager

class BackupManager:
    def __init__(self):
        self.catalog_manager = CatalogManager()
        self.cancel_flag = threading.Event()
        self.open_files_handler = OpenFilesHandler()
    
    def create_backup(self, source_folders, destination_path, compression_type="zip", 
                     include_subdirs=True, progress_callback=None, backup_title="", incremental=False):
        """
        Create a compressed backup of the specified folders.
        
        Args:
            source_folders: List of folder paths to backup
            destination_path: Destination directory for backup
            compression_type: 'zip' or 'tar.gz'
            include_subdirs: Whether to include subdirectories
            progress_callback: Function to call with progress updates
            backup_title: Custom title for the backup
            incremental: Only backup files newer than last backup
        
        Returns:
            str: Backup filename if successful, None if failed
        """
        backup_path = None
        try:
            self.cancel_flag.clear()
            
            # Generate backup name with timestamp and custom title
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "incremental_" if incremental else ""
            if backup_title:
                # Sanitize title and create name
                safe_title = backup_title.replace(" ", "_").replace("-", "_")
                backup_name = f"{prefix}{safe_title}_{timestamp}"
            else:
                backup_name = f"{prefix}backup_{timestamp}"
            
            if compression_type == "zip":
                backup_filename = f"{backup_name}.zip"
            else:
                backup_filename = f"{backup_name}.tar.gz"
            
            backup_path = os.path.join(destination_path, backup_filename)
            
            # Calculate total size for progress tracking with detailed progress
            if progress_callback:
                progress_callback(0, 100, "Coletando lista de arquivos...")
            
            total_size = 0
            file_list = []
            processed_folders = 0
            
            # First pass: collect all files
            for i, source_folder in enumerate(source_folders):
                if self.cancel_flag.is_set():
                    return None
                
                if progress_callback:
                    progress_callback((i / len(source_folders)) * 30, 100, 
                                    f"Analisando pasta: {os.path.basename(source_folder)}")
                
                # Get last backup timestamp for incremental mode
                last_backup_time = None
                if incremental:
                    last_backup_time = self._get_last_backup_time(source_folders)
                    if progress_callback and last_backup_time:
                        progress_callback(0, 100, f"Modo incremental: desde {last_backup_time.strftime('%d/%m/%Y %H:%M')}")
                
                folder_files = self._get_files_to_backup(source_folder, include_subdirs, last_backup_time)
                file_list.extend(folder_files)
                processed_folders += 1
            
            if progress_callback:
                progress_callback(30, 100, f"Calculando tamanho de {len(file_list)} arquivos...")
            
            # Second pass: calculate sizes with progress
            for i, file_path in enumerate(file_list):
                if self.cancel_flag.is_set():
                    return None
                
                try:
                    total_size += get_file_size(file_path)
                    
                    # Update progress every 100 files or at the end
                    if i % 100 == 0 or i == len(file_list) - 1:
                        if progress_callback:
                            progress_pct = 30 + ((i + 1) / len(file_list)) * 50  # 30-80%
                            progress_callback(progress_pct, 100, 
                                            f"Calculando tamanho: {i+1}/{len(file_list)} arquivos")
                            
                except (OSError, IOError):
                    continue
            
            if progress_callback:
                progress_callback(80, 100, f"Tamanho total: {format_size(total_size)}")
                
            # Small delay to show final calculation result
            import time
            time.sleep(0.5)
            
            if not file_list:
                message = "Nenhum arquivo novo encontrado para backup incremental" if incremental else "No files found to backup"
                raise Exception(message)
            
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
                    'incremental': incremental,
                    'files': [{'name': f, 'size': get_file_size(f)} for f in file_list if os.path.exists(f)]
                }
                
                self.catalog_manager.add_catalog_entry(catalog_entry)
                
                # Update user statistics
                backup_size = get_file_size(backup_path)
                user_manager.update_backup_stats(backup_size)
                
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
            try:
                if backup_path and os.path.exists(backup_path):
                    os.remove(backup_path)
            except:
                pass
            raise Exception(f"Backup failed: {str(e)}")
    
    def _get_files_to_backup(self, source_folder, include_subdirs, since_time=None):
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
                            if self._should_include_file(file_path, since_time):
                                files.append(file_path)
            else:
                for item in os.listdir(source_folder):
                    item_path = os.path.join(source_folder, item)
                    if os.path.isfile(item_path):
                        if self._should_include_file(item_path, since_time):
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
    
    def _get_last_backup_time(self, source_folders):
        """Obter timestamp do último backup para as pastas especificadas."""
        try:
            catalog = self.catalog_manager.get_catalog_entries()
            if not catalog:
                return None
            
            # Procurar pelo backup mais recente das mesmas pastas
            last_backup_time = None
            source_folders_set = set(str(Path(f).resolve()) for f in source_folders)
            
            for entry in catalog:
                entry_folders = entry.get('source_folders', [])
                entry_folders_set = set(str(Path(f).resolve()) for f in entry_folders)
                
                # Se as pastas são as mesmas ou subconjunto
                if source_folders_set.intersection(entry_folders_set):
                    backup_date = entry.get('date')
                    if backup_date:
                        try:
                            backup_time = datetime.fromisoformat(backup_date)
                            if not last_backup_time or backup_time > last_backup_time:
                                last_backup_time = backup_time
                        except:
                            continue
            
            return last_backup_time
        except Exception as e:
            print(f"Erro ao obter última data de backup: {e}")
            return None
    
    def _should_include_file(self, file_path, since_time):
        """Verificar se arquivo deve ser incluído baseado na data de modificação."""
        try:
            # Se não há filtro de tempo, incluir sempre
            if since_time is None:
                return True
            
            # Verificar data de modificação do arquivo
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            return file_mtime > since_time
            
        except (OSError, IOError):
            # Se não conseguir acessar o arquivo, incluir por segurança
            return True
    
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
