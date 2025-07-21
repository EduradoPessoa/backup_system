#!/usr/bin/env python3
"""
Desktop Backup Application
Main entry point for the backup application with tkinter GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_components import BackupGUI

def main():
    """Main function to start the backup application."""
    try:
        # Create the main window
        root = tk.Tk()
        root.title("Desktop Backup Manager - PHOENYX TECNOLOGIA 2025")
        root.geometry("800x600")
        root.minsize(600, 400)
        
        # Set application icon (using default for cross-platform compatibility)
        try:
            root.iconname("Backup Manager")
        except:
            pass
        
        # Initialize the main GUI
        app = BackupGUI(root)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
