"""
Utility functions for Desktop Backup Application
Common helper functions used throughout the application.
"""

import os
import stat
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: File size in bytes, 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return 0

def format_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def format_time(timestamp):
    """
    Format timestamp for display.
    
    Args:
        timestamp: datetime object or ISO string
        
    Returns:
        str: Formatted time string
    """
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create directory {directory_path}: {str(e)}")

def calculate_directory_size(directory_path):
    """
    Calculate the total size of a directory recursively.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += get_file_size(file_path)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    except (OSError, IOError):
        # Skip directories that can't be accessed
        pass
    
    return total_size

def is_file_readable(file_path):
    """
    Check if a file is readable.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file is readable, False otherwise
    """
    try:
        return os.access(file_path, os.R_OK)
    except:
        return False

def is_directory_writable(directory_path):
    """
    Check if a directory is writable.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        bool: True if directory is writable, False otherwise
    """
    try:
        return os.access(directory_path, os.W_OK)
    except:
        return False

def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Characters not allowed in filenames on Windows
    invalid_chars = '<>:"/\\|?*'
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove trailing dots and spaces
    sanitized = sanitized.rstrip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized

def get_available_space(path):
    """
    Get available disk space at the given path.
    
    Args:
        path: Path to check
        
    Returns:
        int: Available space in bytes
    """
    try:
        statvfs = os.statvfs(path)
        return statvfs.f_frsize * statvfs.f_bavail
    except:
        try:
            # Fallback for Windows
            import shutil
            return shutil.disk_usage(path).free
        except:
            return 0

def calculate_file_hash(file_path, algorithm='md5'):
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        str: Hex digest of the hash
    """
    try:
        if algorithm == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm == 'sha1':
            hash_obj = hashlib.sha1()
        elif algorithm == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except Exception as e:
        raise Exception(f"Failed to calculate hash: {str(e)}")

def copy_file_with_progress(src, dst, progress_callback=None):
    """
    Copy a file with progress reporting.
    
    Args:
        src: Source file path
        dst: Destination file path
        progress_callback: Function to call with progress updates
    """
    try:
        file_size = get_file_size(src)
        copied_size = 0
        
        ensure_directory_exists(os.path.dirname(dst))
        
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                chunk = fsrc.read(64 * 1024)  # 64KB chunks
                if not chunk:
                    break
                
                fdst.write(chunk)
                copied_size += len(chunk)
                
                if progress_callback and file_size > 0:
                    progress = (copied_size / file_size) * 100
                    progress_callback(progress, os.path.basename(src))
        
        # Copy file permissions
        try:
            shutil.copystat(src, dst)
        except:
            pass  # Ignore permission errors
            
    except Exception as e:
        raise Exception(f"Failed to copy file: {str(e)}")

def validate_backup_name(name):
    """
    Validate a backup name.
    
    Args:
        name: Backup name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name.strip()) == 0:
        return False
    
    # Check for invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        if char in name:
            return False
    
    # Check length
    if len(name) > 255:
        return False
    
    return True

def get_temp_directory():
    """
    Get a temporary directory for backup operations.
    
    Returns:
        str: Path to temporary directory
    """
    import tempfile
    
    temp_dir = os.path.join(tempfile.gettempdir(), "backup_manager")
    ensure_directory_exists(temp_dir)
    return temp_dir

def cleanup_temp_files(temp_dir=None):
    """
    Clean up temporary files.
    
    Args:
        temp_dir: Specific temporary directory to clean, or None for default
    """
    if temp_dir is None:
        temp_dir = get_temp_directory()
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except:
        pass  # Ignore cleanup errors

def is_backup_file(file_path):
    """
    Check if a file is a valid backup file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if it's a backup file, False otherwise
    """
    backup_extensions = ['.zip', '.tar.gz', '.tar', '.7z']
    
    file_path_lower = file_path.lower()
    return any(file_path_lower.endswith(ext) for ext in backup_extensions)

def get_backup_type(file_path):
    """
    Determine the backup type from file extension.
    
    Args:
        file_path: Path to the backup file
        
    Returns:
        str: Backup type ('zip', 'tar.gz', 'unknown')
    """
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith('.zip'):
        return 'zip'
    elif file_path_lower.endswith('.tar.gz'):
        return 'tar.gz'
    elif file_path_lower.endswith('.tar'):
        return 'tar'
    else:
        return 'unknown'

def estimate_compression_ratio(file_path):
    """
    Estimate compression ratio for a file or directory.
    
    Args:
        file_path: Path to file or directory
        
    Returns:
        float: Estimated compression ratio (0.1 to 1.0)
    """
    # Simple heuristic based on file types
    text_extensions = ['.txt', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    compressed_extensions = ['.zip', '.rar', '.7z', '.gz', '.bz2']
    
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in text_extensions:
            return 0.3  # Text files compress well
        elif ext in image_extensions:
            return 0.9  # Images don't compress much
        elif ext in compressed_extensions:
            return 1.0  # Already compressed
        else:
            return 0.6  # Average compression
    else:
        # For directories, return average
        return 0.6
