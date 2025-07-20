# Desktop Backup Manager

## Overview

This is a desktop backup application built with Python and tkinter that provides a comprehensive solution for creating, managing, and restoring compressed backups. The application features a tabbed GUI interface for backup creation, restoration, catalog management, and settings configuration.

## User Preferences

Preferred communication style: Simple, everyday language.
User language: Portuguese (user requested in Portuguese).

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **GUI Layer**: tkinter-based interface with tabbed navigation
- **Business Logic Layer**: Separate managers for backup, restore, and catalog operations
- **Utility Layer**: Common helper functions for file operations
- **Data Storage**: JSON-based catalog system for backup metadata

The architecture emphasizes modularity, making it easy to extend functionality and maintain individual components independently.

## Key Components

### BackupManager (`backup_manager.py`)
- **Purpose**: Handles creation of compressed backups (ZIP and TAR.GZ formats)
- **Key Features**: 
  - Multi-folder backup support
  - Progress tracking with callback mechanism
  - Cancellation support via threading events
  - Integration with catalog management

### RestoreManager (`restore_manager.py`)
- **Purpose**: Manages restoration of files from backup archives
- **Key Features**:
  - Support for both ZIP and TAR.GZ formats
  - Backup content inspection before restoration
  - Selective file restoration capabilities

### CatalogManager (`catalog_manager.py`)
- **Purpose**: Manages backup metadata and application settings
- **Storage Location**: User home directory (`~/.backup_manager/catalogs/`)
- **Data Format**: JSON files for catalog and settings storage
- **Key Features**:
  - Automatic catalog initialization
  - Backup history tracking
  - Settings persistence

### BackupGUI (`gui_components.py`)
- **Purpose**: Main GUI interface with tabbed navigation
- **Framework**: tkinter with ttk widgets for modern appearance
- **Layout**: Four main tabs (Backup, Restore, Catalog, Settings)
- **Features**: 
  - Progress tracking during operations
  - Multi-folder selection
  - Real-time status updates

### Utils (`utils.py`)
- **Purpose**: Common utility functions used across components
- **Key Functions**:
  - File size calculation and formatting
  - Directory operations
  - Time formatting utilities

## Data Flow

1. **Backup Creation**:
   - User selects source folders via GUI
   - BackupManager compresses selected folders
   - Progress updates sent to GUI via callbacks
   - Backup metadata stored in catalog
   - Completion status reported to user

2. **Backup Restoration**:
   - User selects backup from catalog or file system
   - RestoreManager inspects backup contents
   - User selects specific files/folders to restore
   - Files extracted to specified destination
   - Progress tracked and reported

3. **Catalog Management**:
   - All backup operations logged to JSON catalog
   - Settings stored separately in JSON format
   - Automatic catalog initialization on first run

## External Dependencies

- **Standard Library Only**: The application relies entirely on Python standard library components
- **GUI Framework**: tkinter (built into Python)
- **Archive Formats**: zipfile and tarfile modules
- **Threading**: Built-in threading module for background operations
- **File Operations**: pathlib and os modules for cross-platform file handling

This design choice ensures maximum compatibility and eliminates external dependency management.

## Deployment Strategy

The application is designed as a standalone desktop application:

- **Distribution**: Single Python script execution via `main.py`
- **Installation**: No installation required - can run directly from source
- **Cross-Platform**: Compatible with Windows, macOS, and Linux
- **Data Storage**: Uses user home directory for settings and catalogs
- **Packaging**: Can be packaged using tools like PyInstaller for executable distribution

The modular structure allows for easy maintenance and feature additions while keeping the deployment process simple and straightforward.