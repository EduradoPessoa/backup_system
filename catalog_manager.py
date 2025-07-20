"""
Catalog Manager for Desktop Backup Application
Manages backup catalogs and metadata storage.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import shutil

from utils import ensure_directory_exists, get_file_size

class CatalogManager:
    def __init__(self, catalog_dir=None):
        if catalog_dir is None:
            # Default catalog directory in user's home
            home_dir = Path.home()
            self.catalog_dir = home_dir / ".backup_manager" / "catalogs"
        else:
            self.catalog_dir = Path(catalog_dir)
        
        # Ensure catalog directory exists
        ensure_directory_exists(str(self.catalog_dir))
        
        self.catalog_file = self.catalog_dir / "backup_catalog.json"
        self.settings_file = self.catalog_dir / "settings.json"
        
        # Initialize catalog if it doesn't exist
        self._initialize_catalog()
    
    def _initialize_catalog(self):
        """Initialize the catalog file if it doesn't exist."""
        if not self.catalog_file.exists():
            initial_catalog = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'backups': []
            }
            self._save_catalog(initial_catalog)
    
    def _load_catalog(self):
        """Load catalog from file."""
        try:
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return empty catalog if file doesn't exist or is corrupted
            return {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'backups': []
            }
    
    def _save_catalog(self, catalog_data):
        """Save catalog to file."""
        try:
            # Create backup of existing catalog
            if self.catalog_file.exists():
                backup_file = self.catalog_file.with_suffix('.json.bak')
                shutil.copy2(self.catalog_file, backup_file)
            
            # Save new catalog
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Failed to save catalog: {str(e)}")
    
    def add_catalog_entry(self, backup_info):
        """
        Add a new backup entry to the catalog.
        
        Args:
            backup_info: Dictionary containing backup information
        """
        try:
            catalog = self._load_catalog()
            
            # Validate backup info
            required_fields = ['name', 'filename', 'path', 'date', 'size', 'compression']
            for field in required_fields:
                if field not in backup_info:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add additional metadata
            backup_entry = backup_info.copy()
            backup_entry['id'] = self._generate_backup_id()
            backup_entry['created'] = datetime.now().isoformat()
            
            # Verify backup file exists
            if not os.path.exists(backup_info['path']):
                raise Exception(f"Backup file not found: {backup_info['path']}")
            
            # Update file size if different
            actual_size = get_file_size(backup_info['path'])
            backup_entry['size'] = actual_size
            
            # Add to catalog
            catalog['backups'].append(backup_entry)
            
            # Sort by date (newest first)
            catalog['backups'].sort(key=lambda x: x['date'], reverse=True)
            
            # Save catalog
            self._save_catalog(catalog)
            
        except Exception as e:
            raise Exception(f"Failed to add catalog entry: {str(e)}")
    
    def get_catalog_entries(self):
        """Get all catalog entries."""
        try:
            catalog = self._load_catalog()
            entries = []
            
            for backup in catalog['backups']:
                # Verify backup file still exists
                if os.path.exists(backup['path']):
                    entries.append({
                        'id': backup.get('id', ''),
                        'name': backup['name'],
                        'filename': backup['filename'],
                        'path': backup['path'],
                        'date': backup['date'],
                        'size': backup['size'],
                        'compression': backup['compression'],
                        'file_count': backup.get('file_count', 0),
                        'location': os.path.dirname(backup['path']),
                        'source_folders': backup.get('source_folders', [])
                    })
                else:
                    # Mark as missing but keep in catalog
                    entry = backup.copy()
                    entry['status'] = 'missing'
                    entry['location'] = f"MISSING: {os.path.dirname(backup['path'])}"
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            raise Exception(f"Failed to get catalog entries: {str(e)}")
    
    def get_backup_list(self):
        """Get simplified backup list for UI display."""
        try:
            entries = self.get_catalog_entries()
            backup_list = []
            
            for entry in entries:
                if entry.get('status') != 'missing':
                    backup_list.append({
                        'name': entry['name'],
                        'filename': entry['filename'],
                        'path': entry['path'],
                        'date': entry['date'],
                        'size': entry['size']
                    })
            
            return backup_list
            
        except Exception as e:
            raise Exception(f"Failed to get backup list: {str(e)}")
    
    def delete_catalog_entry(self, backup_name):
        """
        Delete a catalog entry by backup name.
        
        Args:
            backup_name: Name of the backup to delete
        """
        try:
            catalog = self._load_catalog()
            
            # Find and remove the backup entry
            original_count = len(catalog['backups'])
            catalog['backups'] = [b for b in catalog['backups'] if b['name'] != backup_name]
            
            if len(catalog['backups']) == original_count:
                raise Exception(f"Backup not found: {backup_name}")
            
            # Save updated catalog
            self._save_catalog(catalog)
            
        except Exception as e:
            raise Exception(f"Failed to delete catalog entry: {str(e)}")
    
    def update_catalog_entry(self, backup_name, updates):
        """
        Update a catalog entry.
        
        Args:
            backup_name: Name of the backup to update
            updates: Dictionary of fields to update
        """
        try:
            catalog = self._load_catalog()
            
            # Find and update the backup entry
            updated = False
            for backup in catalog['backups']:
                if backup['name'] == backup_name:
                    backup.update(updates)
                    backup['modified'] = datetime.now().isoformat()
                    updated = True
                    break
            
            if not updated:
                raise Exception(f"Backup not found: {backup_name}")
            
            # Save updated catalog
            self._save_catalog(catalog)
            
        except Exception as e:
            raise Exception(f"Failed to update catalog entry: {str(e)}")
    
    def get_backup_info(self, backup_name):
        """
        Get detailed information about a specific backup.
        
        Args:
            backup_name: Name of the backup
            
        Returns:
            dict: Backup information or None if not found
        """
        try:
            catalog = self._load_catalog()
            
            for backup in catalog['backups']:
                if backup['name'] == backup_name:
                    return backup
            
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get backup info: {str(e)}")
    
    def cleanup_missing_backups(self):
        """Remove catalog entries for missing backup files."""
        try:
            catalog = self._load_catalog()
            
            # Filter out backups with missing files
            original_count = len(catalog['backups'])
            catalog['backups'] = [b for b in catalog['backups'] if os.path.exists(b['path'])]
            
            removed_count = original_count - len(catalog['backups'])
            
            if removed_count > 0:
                self._save_catalog(catalog)
            
            return removed_count
            
        except Exception as e:
            raise Exception(f"Failed to cleanup missing backups: {str(e)}")
    
    def export_catalog(self, export_path):
        """
        Export catalog to a file.
        
        Args:
            export_path: Path to export the catalog to
        """
        try:
            catalog = self._load_catalog()
            
            # Create export data with additional metadata
            export_data = {
                'export_date': datetime.now().isoformat(),
                'catalog_version': catalog.get('version', '1.0'),
                'total_backups': len(catalog['backups']),
                'catalog': catalog
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Failed to export catalog: {str(e)}")
    
    def import_catalog(self, import_path, merge=True):
        """
        Import catalog from a file.
        
        Args:
            import_path: Path to import the catalog from
            merge: Whether to merge with existing catalog or replace
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'catalog' in import_data:
                imported_catalog = import_data['catalog']
            else:
                imported_catalog = import_data
            
            if merge:
                # Merge with existing catalog
                current_catalog = self._load_catalog()
                
                # Add imported backups, avoiding duplicates
                existing_names = {b['name'] for b in current_catalog['backups']}
                
                for backup in imported_catalog.get('backups', []):
                    if backup['name'] not in existing_names:
                        current_catalog['backups'].append(backup)
                
                # Sort by date
                current_catalog['backups'].sort(key=lambda x: x['date'], reverse=True)
                
                self._save_catalog(current_catalog)
            else:
                # Replace existing catalog
                self._save_catalog(imported_catalog)
                
        except Exception as e:
            raise Exception(f"Failed to import catalog: {str(e)}")
    
    def _generate_backup_id(self):
        """Generate a unique backup ID."""
        import uuid
        return str(uuid.uuid4())
    
    def get_statistics(self):
        """Get catalog statistics."""
        try:
            catalog = self._load_catalog()
            
            total_backups = len(catalog['backups'])
            total_size = sum(b['size'] for b in catalog['backups'] if os.path.exists(b['path']))
            missing_backups = sum(1 for b in catalog['backups'] if not os.path.exists(b['path']))
            
            # Group by compression type
            compression_stats = {}
            for backup in catalog['backups']:
                comp_type = backup.get('compression', 'unknown')
                if comp_type not in compression_stats:
                    compression_stats[comp_type] = {'count': 0, 'size': 0}
                compression_stats[comp_type]['count'] += 1
                if os.path.exists(backup['path']):
                    compression_stats[comp_type]['size'] += backup['size']
            
            return {
                'total_backups': total_backups,
                'total_size': total_size,
                'missing_backups': missing_backups,
                'available_backups': total_backups - missing_backups,
                'compression_stats': compression_stats,
                'catalog_file': str(self.catalog_file),
                'catalog_size': get_file_size(str(self.catalog_file)) if self.catalog_file.exists() else 0
            }
            
        except Exception as e:
            raise Exception(f"Failed to get statistics: {str(e)}")
