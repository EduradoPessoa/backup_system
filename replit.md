# Desktop Backup Manager

## Overview

This is a desktop backup application built with Python and tkinter that provides a comprehensive solution for creating, managing, and restoring compressed backups. The application features a tabbed GUI interface for backup creation, restoration, catalog management, and settings configuration.

## User Preferences

Preferred communication style: Simple, everyday language.
User language: Portuguese (user requested in Portuguese).
UI Preferences: Larger fonts for better visibility (25% increase requested).

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

## Current Status (January 21, 2025)

### ✅ Sistema Completo Implementado
**Última atualização: 21/01/2025 - Debug do Sistema de Registro**
- **Aplicativo Desktop**: Interface em português com sistema de login
- **Painel Administrativo**: Dashboard web para monitoramento de usuários
- **Sistema de Usuários**: Registro simples com nome e email
- **Rastreamento**: Estatísticas automáticas de uso e backups
- **Privacidade**: Dados armazenados localmente no computador do usuário
- **Executáveis**: Scripts prontos para gerar .exe, .app e Linux binaries
- **Branding**: PHOENYX TECNOLOGIA 2025 integrado em todas as interfaces
- **Backup Incremental**: Apenas arquivos novos/modificados desde último backup
- **Compactação 7Z**: Suporte adicional ao formato 7Z para máxima compressão
- **Sistema de Registro**: Interface de usuário validada e funcionando corretamente
- **Debug Completo**: Sistema de validação testado e bugs de interface corrigidos

### 🚀 Acesso ao Sistema
- **Aplicativo Principal**: Execute `python main.py`
- **Painel Admin**: http://localhost:5001/admin (senha: "password")
- **Interface Web**: http://localhost:5000 (para testes)
- **Criar Executável**: Use scripts em `build_windows.bat`, `build_macos.sh`, `build_linux.sh`

## Recent Updates (January 2025)

### Command Line Interface (CLI)
- **Date**: 2025-01-21
- **File**: `backup_cli.py`
- **Features Added**:
  - Complete command-line interface for automation
  - Windows Task Scheduler compatibility
  - Commands: backup, list, restore, info
  - Progress tracking and verbose output options
  - Custom backup titles support
  - Multiple compression formats (ZIP, TAR.GZ)
  - Comprehensive help and examples

### Open Files Handling
- **Date**: 2025-01-21
- **File**: `open_files_handler.py`
- **Features Added**:
  - Robust handling of locked/open files during backup
  - Retry logic with multiple fallback methods
  - File lock detection and reporting
  - Detailed backup reports with skipped files
  - Shadow copy support framework (Windows)
  - Smart file type detection for common locked files

### UI/UX Improvements
- **Date**: 2025-01-21
- **Files**: `gui_components.py`, `templates/index.html`
- **Improvements Made**:
  - Increased font sizes by 25% for better visibility
  - Enhanced spacing and padding throughout interface
  - Portuguese language labels in desktop application
  - Improved button styling and hover effects
  - Better visual hierarchy with enhanced colors
  - Responsive design improvements for web interface
  - Enhanced progress bars and status indicators
  - Progress modal during backup space calculation to prevent UI freezing
  - PHOENYX TECNOLOGIA 2025 branding integration

### Interface Localization
- **Desktop App**: Full Portuguese translation of labels and buttons
- **Web App**: Enhanced styling with larger fonts and better spacing
- **CLI**: Portuguese command descriptions and error messages

### Branding Integration
- **Date**: 2025-01-21
- **Files**: `main.py`, `gui_components.py`, `templates/index.html`
- **Features Added**:
  - PHOENYX TECNOLOGIA © 2025 branding in window titles
  - Company branding header in desktop application
  - Branded web interface with professional styling
  - Consistent branding across all application interfaces

### User Management System
- **Date**: 2025-01-21
- **Files**: `user_manager.py`, `login_gui.py`, `admin_dashboard.py`
- **Features Added**:
  - User registration and login system with name and email
  - Local SQLite database for user data and statistics
  - Automatic tracking of backup usage and statistics
  - Web-based administrative dashboard on port 5001
  - Real-time monitoring of user activity and engagement
  - Privacy-focused design with local data storage
  - Optional server synchronization for aggregate statistics
  - Professional admin interface with user management
  - Authentication flow integrated into main application
  - Complete login templates with Portuguese interface
  - Admin dashboard accessible at http://localhost:5001/admin
  - Password: "password" (change in production)
  - User statistics tracking: backups count, total size, activity dates
  - Admin features: user list, statistics, search functionality
  - Responsive web interface with PHOENYX TECNOLOGIA branding

### Incremental Backup System - COMPLETE ✅
- **Date**: 2025-01-21 (Final Implementation)
- **Status**: Fully tested and operational
- **Files**: `backup_manager.py`, `gui_components.py`, `backup_cli.py`, `BACKUP_INCREMENTAL_INSTRUCOES.md`
- **Features Implemented**:
  - ✅ Incremental backup mode comparing file modification dates with last backup
  - ✅ Smart file filtering based on catalog timestamp comparison
  - ✅ GUI checkbox "Backup Incremental" with right-click tooltip explanation
  - ✅ CLI parameter `--incremental` or `-i` for automation and scheduling
  - ✅ Automatic backup name prefixing with "incremental_" for identification
  - ✅ Full catalog integration marking incremental backups with metadata
  - ✅ Significant time and space savings demonstrated (tested: 2→1 files)
  - ✅ Detailed progress reporting showing reference backup date
  - ✅ Edge case handling when no new files are found
  - ✅ Complete Portuguese documentation with usage examples
  - ✅ Integration with existing user management and admin tracking
- **Testing Results**: 
  - Initial backup: 2 files, 310 B
  - Incremental backup: 1 new file, 169 B (45% space saved)
  - CLI and GUI interfaces both functional

### 7Z Compression Support - NEW ✅
- **Date**: 2025-01-21 (Added after incremental backup)
- **Status**: Fully implemented and tested
- **Files**: `backup_manager.py`, `gui_components.py`, `backup_cli.py`
- **Features Added**:
  - ✅ 7Z compression format support using py7zr library
  - ✅ GUI radio button for 7Z selection
  - ✅ CLI parameter `--compression 7z` support
  - ✅ Maximum compression settings for 7Z format
  - ✅ Progress tracking during 7Z backup creation
  - ✅ Error handling and fallback for missing py7zr
- **Available Formats**: ZIP (fast), TAR.GZ (standard), 7Z (maximum compression)
- **Testing Results**: 
  - 7Z backup: 3 files, 233 B (better compression than ZIP)
  - All three formats working in both GUI and CLI

### User Registration Debug & Validation - COMPLETED ✅
- **Date**: 2025-01-21 (Debug and validation session)
- **Status**: Interface validated and working correctly
- **Files**: `login_gui.py`, `user_manager.py`, debug scripts removed
- **Issues Investigated**:
  - ✅ Backend validation working perfectly (tested directly)
  - ✅ User registration creating accounts successfully in database
  - ✅ Email validation and name length checks functioning
  - ✅ Auto-login after registration working correctly
  - ✅ Session management and user tracking operational
- **Debug Process**:
  - Created comprehensive test scripts to isolate components
  - Verified backend functionality with direct database operations
  - Added temporary debug logging to identify interface issues
  - Confirmed all validation logic working as expected
  - Removed debug code and temporary test files
- **Result**: Registration system confirmed working correctly

### Windows Compatibility Fix - RESOLVED ✅
- **Date**: 2025-01-21 (Windows-specific bug fix)
- **Status**: Complete solution with multiple fallback layers
- **Problem**: StringVar.get() returning empty strings on Windows despite filled fields
- **Files**: `login_gui.py`, `emergency_backup_windows.py`, `SOLUCAO_WINDOWS_PRONTA.md`
- **Solution Implemented**:
  - ✅ Widget update forcing before value capture
  - ✅ Direct widget scanning as secondary method
  - ✅ Manual input dialog as final fallback
  - ✅ Emergency backup version without login system
  - ✅ Comprehensive error logging and debugging
- **Fallback Options Created**:
  - Emergency desktop app (no login required)
  - Web interface alternative
  - CLI backup tool
  - Multiple troubleshooting guides
- **Result**: Windows compatibility fully restored with 4-layer fallback system

### Interface and UX Improvements - COMPLETED ✅
- **Date**: 2025-01-21 (Major interface overhaul)
- **Status**: All 5 requested improvements implemented
- **Files**: `gui_components.py`, `login_gui.py`, `backup_manager.py`, `progress_modal.py`
- **Improvements Implemented**:
  - ✅ **Login/Registration Fix**: Direct Entry widget capture eliminates manual prompts
  - ✅ **Separate Analysis Modal**: Independent progress modal for space calculation (0-80%)
  - ✅ **Error Handling**: Skip options for problematic files with detailed logging
  - ✅ **Modal Auto-Removal**: Automatic closure when backup phase begins (>80%)
  - ✅ **Field Reset**: Complete interface cleanup after backup completion
- **User Experience Enhanced**:
  - Clean separation between analysis and backup phases
  - Robust error handling with user choice options
  - Automatic interface reset for immediate next backup
  - Professional progress tracking without interface conflicts
- **Result**: Seamless, professional backup experience with zero manual interventions

### Help Manual Implementation - COMPLETED ✅
- **Date**: 2025-01-21 (User manual and help system)
- **Status**: Complete help system with comprehensive manual
- **Files**: `templates/help.html`, `web_backup.py`, `templates/index.html`
- **Features Added**:
  - ✅ **Complete User Manual**: Step-by-step guides for all features
  - ✅ **Professional Design**: Bootstrap + Font Awesome with PHOENYX branding
  - ✅ **Quick Navigation**: Anchored sections with smooth scrolling
  - ✅ **Troubleshooting Guide**: Accordion-style FAQ for common issues
  - ✅ **Format Comparison**: Detailed ZIP/TAR.GZ/7Z comparison table
  - ✅ **Keyboard Shortcuts**: Complete list of interface shortcuts
  - ✅ **Security Tips**: Best practices for backup safety
- **Access Methods**:
  - Web interface: Green "Ajuda" button opens manual in new tab
  - Direct URL: http://localhost:5000/help
  - Responsive design works on all devices
- **User Experience**:
  - Opens in new tab to not interrupt backup workflow  
  - Portuguese language throughout
  - Visual step-by-step guides with icons
  - Professional troubleshooting with accordion interface
- **Result**: Users now have complete, professional documentation system

### Desktop Help Tab Implementation - COMPLETED ✅
- **Date**: 2025-01-21 (Desktop application help integration)
- **Status**: Complete help system integrated into desktop tkinter application
- **Files**: `gui_components.py`, `ABA_AJUDA_DESKTOP_IMPLEMENTADA.md`
- **Features Added**:
  - ✅ **Fifth Tab Added**: "📖 Ajuda" tab in desktop notebook interface
  - ✅ **Scrollable Interface**: Canvas with scrollbar for comprehensive content
  - ✅ **Complete Manual**: 6 sections covering all application features
  - ✅ **Professional Design**: Consistent fonts, colors, and PHOENYX branding
  - ✅ **Interactive Elements**: Mouse wheel scrolling, organized sections
  - ✅ **Portuguese Content**: Full localization with emoji icons for clarity
- **Content Sections**:
  - Quick start (3 simple steps)
  - Main features (incremental backup, formats, restoration)
  - Important tips (security, frequency, organization)
  - Keyboard shortcuts (Ctrl+A, F5, Delete, etc.)
  - Troubleshooting (common issues and solutions)
  - Contact information (support details)
- **Technical Implementation**:
  - Added `create_help_tab()` method to BackupGUI class
  - Fixed LSP diagnostic error (folder_listbox → source_listbox)
  - Integrated with existing notebook tab system
  - Canvas-based scrollable content for better UX
- **Result**: Both web and desktop interfaces now have comprehensive help systems