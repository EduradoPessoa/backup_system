"""
GUI Components for Desktop Backup Application
Contains all the tkinter GUI components and layout logic.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from datetime import datetime

from backup_manager import BackupManager
from restore_manager import RestoreManager
from catalog_manager import CatalogManager
from utils import format_size, format_time

class ProgressModal:
    def __init__(self, parent, title="Progresso"):
        self.parent = parent
        self.cancelled = False
        
        # Create modal window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("450x180")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.window.winfo_screenheight() // 2) - (180 // 2)
        self.window.geometry(f"450x180+{x}+{y}")
        
        # Configure style
        self.window.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        self.title_label = ttk.Label(main_frame, text="Calculando tamanho do backup...", 
                                    font=('Segoe UI', 12, 'bold'))
        self.title_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400, mode='indeterminate')
        self.progress_bar.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Analisando arquivos...", 
                                     font=('Segoe UI', 10))
        self.status_label.pack(pady=(0, 15))
        
        # Cancel button
        self.cancel_button = ttk.Button(main_frame, text="Cancelar", 
                                       command=self.cancel)
        self.cancel_button.pack()
        
        # Start indeterminate progress
        self.progress_bar.start(10)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def update_status(self, message, current=0, total=0):
        """Update the progress status."""
        if self.window.winfo_exists():
            self.status_label.config(text=message)
            
            if total > 0:
                # Switch to determinate mode
                self.progress_bar.stop()
                self.progress_bar.config(mode='determinate')
                progress = (current / total) * 100
                self.progress_var.set(progress)
            
            self.window.update()
    
    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close the modal."""
        if self.window.winfo_exists():
            self.progress_bar.stop()
            self.window.grab_release()
            self.window.destroy()

class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager()
        self.catalog_manager = CatalogManager()
        
        # Variables
        self.source_folders = []
        self.destination_path = tk.StringVar()
        self.backup_in_progress = False
        
        self.setup_gui()
        self.load_settings()
    
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Configure default fonts (25% larger)
        default_font = ('Segoe UI', 11)  # Base font increased from 9 to 11
        heading_font = ('Segoe UI', 14, 'bold')  # Heading font increased from 11 to 14
        button_font = ('Segoe UI', 10)  # Button font increased from 8 to 10
        
        # Configure style for better appearance
        style = ttk.Style()
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=button_font, padding=(10, 5))
        style.configure('TLabelFrame.Label', font=heading_font)
        style.configure('TNotebook.Tab', font=default_font, padding=(15, 8))
        
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # Company branding header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        branding_label = ttk.Label(header_frame, text="PHOENYX TECNOLOGIA © 2025", 
                                  font=('Segoe UI', 10, 'italic'),
                                  foreground='#666666')
        branding_label.pack(anchor='ne')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        # Create tabs
        self.create_backup_tab()
        self.create_restore_tab()
        self.create_catalog_tab()
        self.create_settings_tab()
        self.create_help_tab()
    
    def create_backup_tab(self):
        """Create the backup tab."""
        self.backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backup_frame, text="Backup")
        
        # Source folders section
        source_frame = ttk.LabelFrame(self.backup_frame, text="Pastas de Origem", padding=15)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Source folders listbox with scrollbar
        list_frame = ttk.Frame(source_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.source_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                        font=('Consolas', 10), height=8)
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.source_listbox.xview)
        
        self.source_listbox.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Source buttons
        source_btn_frame = ttk.Frame(source_frame)
        source_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(source_btn_frame, text="Adicionar Pasta", command=self.add_source_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(source_btn_frame, text="Remover Selecionada", command=self.remove_source_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(source_btn_frame, text="Limpar Todas", command=self.clear_source_folders).pack(side=tk.LEFT)
        
        # Backup configuration section
        config_frame = ttk.LabelFrame(self.backup_frame, text="Configuração do Backup", padding=15)
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Backup title
        title_frame = ttk.Frame(config_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Título do Backup:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        self.backup_title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.backup_title_var, width=35, font=('Segoe UI', 10))
        title_entry.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(title_frame, text="(Ex: Documentos_2025, Fotos_Familia)", font=('Segoe UI', 9, 'italic')).pack(side=tk.LEFT, padx=(10, 0))
        
        # Destination section
        dest_frame = ttk.LabelFrame(self.backup_frame, text="Destino", padding=15)
        dest_frame.pack(fill=tk.X, padx=10, pady=10)
        
        dest_entry_frame = ttk.Frame(dest_frame)
        dest_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(dest_entry_frame, textvariable=self.destination_path, width=50, font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(dest_entry_frame, text="Procurar", command=self.browse_destination).pack(side=tk.RIGHT)
        
        # Backup options
        options_frame = ttk.LabelFrame(self.backup_frame, text="Opções do Backup", padding=15)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.compression_var = tk.StringVar(value="zip")
        ttk.Label(options_frame, text="Compactação:", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="ZIP", variable=self.compression_var, value="zip").pack(side=tk.LEFT, padx=(10, 15))
        ttk.Radiobutton(options_frame, text="TAR.GZ", variable=self.compression_var, value="tar.gz").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(options_frame, text="7Z", variable=self.compression_var, value="7z").pack(side=tk.LEFT, padx=(0, 15))
        
        self.include_subdirs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Incluir subpastas", variable=self.include_subdirs_var).pack(side=tk.LEFT, padx=(15, 0))
        
        # Incremental backup option
        self.incremental_var = tk.BooleanVar(value=False)
        incremental_cb = ttk.Checkbutton(options_frame, text="Backup Incremental", variable=self.incremental_var)
        incremental_cb.pack(side=tk.LEFT, padx=(15, 0))
        
        # Tooltip for incremental backup
        def show_incremental_tooltip(event=None):
            try:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Backup Incremental", 
                    "Inclui apenas arquivos novos ou modificados desde o último backup.\n\n" +
                    "• Economiza tempo e espaço\n" +
                    "• Ideal para backups frequentes\n" +
                    "• Compara datas de modificação dos arquivos")
            except:
                pass
        
        incremental_cb.bind("<Button-3>", show_incremental_tooltip)  # Right-click for info
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.backup_frame, text="Progresso", padding=15)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        
        self.status_label = ttk.Label(progress_frame, text="Pronto", font=('Segoe UI', 10))
        self.status_label.pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(self.backup_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.backup_button = ttk.Button(control_frame, text="Iniciar Backup", command=self.start_backup)
        self.backup_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(control_frame, text="Cancelar", command=self.cancel_backup, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
    
    def create_restore_tab(self):
        """Create the restore tab."""
        self.restore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.restore_frame, text="Restore")
        
        # Backup selection
        backup_frame = ttk.LabelFrame(self.restore_frame, text="Select Backup", padding=10)
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Backup list
        self.backup_listbox = tk.Listbox(backup_frame, height=6)
        backup_scrollbar = ttk.Scrollbar(backup_frame, orient=tk.VERTICAL, command=self.backup_listbox.yview)
        self.backup_listbox.configure(yscrollcommand=backup_scrollbar.set)
        
        self.backup_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        backup_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.backup_listbox.bind('<<ListboxSelect>>', self.on_backup_selected)
        
        # Refresh button
        ttk.Button(backup_frame, text="Refresh", command=self.refresh_backup_list).pack(anchor=tk.E, pady=(5, 0))
        
        # File selection
        files_frame = ttk.LabelFrame(self.restore_frame, text="Files in Backup", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for file structure
        tree_frame = ttk.Frame(files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_tree = ttk.Treeview(tree_frame, selectmode=tk.EXTENDED)
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        
        self.file_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        # Configure columns
        self.file_tree['columns'] = ('size', 'modified')
        self.file_tree.heading('#0', text='File/Folder')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('modified', text='Modified')
        
        self.file_tree.column('#0', width=300)
        self.file_tree.column('size', width=100)
        self.file_tree.column('modified', width=150)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Restore destination
        restore_dest_frame = ttk.LabelFrame(self.restore_frame, text="Restore Destination", padding=10)
        restore_dest_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.restore_dest_var = tk.StringVar()
        restore_entry_frame = ttk.Frame(restore_dest_frame)
        restore_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(restore_entry_frame, textvariable=self.restore_dest_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(restore_entry_frame, text="Browse", command=self.browse_restore_destination).pack(side=tk.RIGHT)
        
        # Restore buttons
        restore_btn_frame = ttk.Frame(self.restore_frame)
        restore_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(restore_btn_frame, text="Restore Selected", command=self.restore_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(restore_btn_frame, text="Restore All", command=self.restore_all).pack(side=tk.LEFT)
    
    def create_catalog_tab(self):
        """Create the catalog management tab."""
        self.catalog_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.catalog_frame, text="Catalog")
        
        # Catalog list
        catalog_list_frame = ttk.LabelFrame(self.catalog_frame, text="Backup Catalogs", padding=10)
        catalog_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for catalog
        self.catalog_tree = ttk.Treeview(catalog_list_frame)
        catalog_scrollbar = ttk.Scrollbar(catalog_list_frame, orient=tk.VERTICAL, command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=catalog_scrollbar.set)
        
        # Configure columns
        self.catalog_tree['columns'] = ('date', 'size', 'files', 'location')
        self.catalog_tree.heading('#0', text='Backup Name')
        self.catalog_tree.heading('date', text='Date')
        self.catalog_tree.heading('size', text='Size')
        self.catalog_tree.heading('files', text='Files')
        self.catalog_tree.heading('location', text='Location')
        
        self.catalog_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        catalog_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Catalog buttons
        catalog_btn_frame = ttk.Frame(self.catalog_frame)
        catalog_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(catalog_btn_frame, text="Refresh", command=self.refresh_catalog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(catalog_btn_frame, text="Delete Selected", command=self.delete_catalog_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(catalog_btn_frame, text="Export Catalog", command=self.export_catalog).pack(side=tk.LEFT)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Log display
        log_frame = ttk.LabelFrame(self.settings_frame, text="Operation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Log buttons
        log_btn_frame = ttk.Frame(self.settings_frame)
        log_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_btn_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT)
    
    def create_help_tab(self):
        """Create the help tab."""
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="📖 Ajuda")
        
        # Main help container with scrollbar
        canvas = tk.Canvas(self.help_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.help_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title section
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(title_frame, text="📖 Manual de Uso - PHOENYX Backup Manager", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, text="PHOENYX TECNOLOGIA © 2025", 
                                  font=('Segoe UI', 10, 'italic'), foreground='#666666')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Quick start section
        quick_frame = ttk.LabelFrame(scrollable_frame, text="🚀 Início Rápido - 3 Passos", padding=15)
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        quick_steps = [
            "1️⃣ Na aba 'Backup': Clique em 'Adicionar Pasta' e selecione as pastas que deseja proteger",
            "2️⃣ Defina um 'Título do Backup' descritivo (ex: Documentos_2025, Fotos_Familia)",
            "3️⃣ Escolha a pasta de destino e clique em 'Iniciar Backup' - Pronto!"
        ]
        
        for step in quick_steps:
            step_label = ttk.Label(quick_frame, text=step, font=('Segoe UI', 11), wraplength=550)
            step_label.pack(anchor='w', pady=2)
        
        # Features section
        features_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Recursos Principais", padding=15)
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features = [
            "✅ Backup Incremental: Salva apenas arquivos novos ou modificados",
            "✅ Múltiplos Formatos: ZIP (rápido), TAR.GZ (balanceado), 7Z (máxima compressão)",
            "✅ Gestão Inteligente: Cataloga automaticamente todos os backups criados",
            "✅ Restauração Seletiva: Escolha exatamente quais arquivos restaurar",
            "✅ Interface Amigável: Design simples e intuitivo em português"
        ]
        
        for feature in features:
            feature_label = ttk.Label(features_frame, text=feature, font=('Segoe UI', 11), wraplength=550)
            feature_label.pack(anchor='w', pady=2)
        
        # Usage tips section
        tips_frame = ttk.LabelFrame(scrollable_frame, text="💡 Dicas Importantes", padding=15)
        tips_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tips = [
            "🔒 Segurança: Mantenha backups em locais diferentes (HD externo, nuvem)",
            "📅 Frequência: Execute backups regulares (diário para documentos, semanal para fotos)",
            "🏷️ Organização: Use títulos descritivos para facilitar identificação",
            "💾 Espaço: Backup incremental economiza espaço significativo",
            "⚡ Performance: 7Z é mais lento mas compacta melhor, ZIP é mais rápido"
        ]
        
        for tip in tips:
            tip_label = ttk.Label(tips_frame, text=tip, font=('Segoe UI', 11), wraplength=550)
            tip_label.pack(anchor='w', pady=2)
        
        # Shortcuts section  
        shortcuts_frame = ttk.LabelFrame(scrollable_frame, text="⌨️ Atalhos de Teclado", padding=15)
        shortcuts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        shortcuts = [
            "Ctrl + A: Adicionar pasta nas abas Backup/Restore",
            "Ctrl + R: Atualizar catálogo ou lista de backups",
            "F5: Recarregar informações da aba atual",
            "Delete: Remover item selecionado (quando aplicável)",
            "Enter: Confirmar ação em campos de texto"
        ]
        
        for shortcut in shortcuts:
            shortcut_label = ttk.Label(shortcuts_frame, text=shortcut, font=('Consolas', 10), wraplength=550)
            shortcut_label.pack(anchor='w', pady=2)
        
        # Troubleshooting section
        trouble_frame = ttk.LabelFrame(scrollable_frame, text="🔧 Solução de Problemas", padding=15)
        trouble_frame.pack(fill=tk.X, padx=20, pady=10)
        
        troubleshooting = [
            "❓ Arquivo em uso: Feche programas que possam estar usando os arquivos",
            "❓ Sem espaço: Verifique espaço livre no destino antes do backup", 
            "❓ Backup lento: Use ZIP para velocidade ou 7Z para economia de espaço",
            "❓ Não encontra backup: Verifique se o arquivo ainda existe no local original",
            "❓ Erro de permissão: Execute como administrador se necessário"
        ]
        
        for issue in troubleshooting:
            issue_label = ttk.Label(trouble_frame, text=issue, font=('Segoe UI', 10), wraplength=550)
            issue_label.pack(anchor='w', pady=2)
        
        # Footer
        footer_frame = ttk.Frame(scrollable_frame)
        footer_frame.pack(fill=tk.X, padx=20, pady=20)
        
        footer_label = ttk.Label(footer_frame, 
                               text="Para mais informações visite: phoenyxtecnologia.com\nSuporte: suporte@phoenyxtecnologia.com", 
                               font=('Segoe UI', 9, 'italic'), foreground='#666666', justify='center')
        footer_label.pack(anchor='center')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def add_source_folder(self):
        """Add a source folder for backup."""
        folder = filedialog.askdirectory(title="Select folder to backup")
        if folder:
            if folder not in self.source_folders:
                self.source_folders.append(folder)
                self.source_listbox.insert(tk.END, folder)
                self.log_message(f"Added source folder: {folder}")
            else:
                messagebox.showwarning("Duplicate", "This folder is already in the list.")
    
    def remove_source_folder(self):
        """Remove selected source folders."""
        selected_indices = self.source_listbox.curselection()
        if selected_indices:
            for i in reversed(selected_indices):
                folder = self.source_folders.pop(i)
                self.source_listbox.delete(i)
                self.log_message(f"Removed source folder: {folder}")
        else:
            messagebox.showwarning("No Selection", "Please select folders to remove.")
    
    def clear_source_folders(self):
        """Clear all source folders."""
        if self.source_folders and messagebox.askyesno("Confirm", "Clear all source folders?"):
            self.source_folders.clear()
            self.source_listbox.delete(0, tk.END)
            self.log_message("Cleared all source folders")
    
    def browse_destination(self):
        """Browse for destination directory."""
        folder = filedialog.askdirectory(title="Select backup destination")
        if folder:
            self.destination_path.set(folder)
            self.log_message(f"Set destination: {folder}")
    
    def start_backup(self):
        """Start the backup process."""
        if not self.source_folders:
            messagebox.showerror("Erro", "Por favor, selecione pelo menos uma pasta de origem.")
            return
        
        if not self.destination_path.get():
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino.")
            return
            
        if not self.backup_title_var.get().strip():
            messagebox.showerror("Erro", "Por favor, insira um título para o backup.")
            return
        
        if not os.path.exists(self.destination_path.get()):
            messagebox.showerror("Erro", "A pasta de destino não existe.")
            return
        
        # Criar modal separado para análise de espaço
        self.calculation_modal = ProgressModal(self.root, "Analisando Espaço")
        
        # Desabilitar botão e habilitar cancelar
        self.backup_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.backup_in_progress = True
        
        # Iniciar backup em thread separada
        backup_thread = threading.Thread(target=self.run_backup, daemon=True)
        backup_thread.start()
    
    def run_backup(self):
        """Executar processo de backup em thread separada."""
        try:
            calculation_phase = True
            
            def progress_callback(current, total, message):
                nonlocal calculation_phase
                progress = (current / total) * 100 if total > 0 else 0
                
                # Fase de cálculo (0-80%) - apenas modal progride
                if calculation_phase and progress <= 80:
                    if hasattr(self, 'calculation_modal'):
                        self.root.after(0, lambda p=progress, m=message: 
                                      self.calculation_modal.update_status(m, p, 100))
                        
                        # Verificar cancelamento
                        if self.calculation_modal.cancelled:
                            self.backup_manager.cancel_backup()
                            return
                
                # Iniciar backup real (>80%) - fechar modal e usar progresso principal
                elif calculation_phase and progress > 80:
                    calculation_phase = False
                    if hasattr(self, 'calculation_modal'):
                        self.root.after(0, lambda: self.calculation_modal.close())
                        delattr(self, 'calculation_modal')
                    # Atualizar progresso principal
                    self.root.after(0, lambda p=progress, m=message: 
                                  self.update_progress(p, m))
                
                # Fase de backup - apenas progresso principal
                elif not calculation_phase:
                    self.root.after(0, lambda p=progress, m=message: 
                                  self.update_progress(p, m))
            
            backup_name = self.backup_manager.create_backup(
                self.source_folders,
                self.destination_path.get(),
                self.compression_var.get(),
                self.include_subdirs_var.get(),
                progress_callback,
                self.backup_title_var.get().strip(),
                self.incremental_var.get()
            )
            
            # Garantir que modal seja fechado
            if hasattr(self, 'calculation_modal'):
                self.root.after(0, lambda: self.calculation_modal.close())
                delattr(self, 'calculation_modal')
            
            if backup_name and self.backup_in_progress:
                self.root.after(0, lambda: self.backup_completed(backup_name))
            elif self.backup_in_progress:
                self.root.after(0, lambda: self.backup_failed("Backup falhou"))
                
        except Exception as e:
            # Garantir fechamento do modal em caso de erro
            if hasattr(self, 'calculation_modal'):
                self.root.after(0, lambda: self.calculation_modal.close())
                delattr(self, 'calculation_modal')
            
            # Log do erro e perguntar se pula
            error_msg = str(e)
            self.log_message(f"ERRO: {error_msg}")
            
            if self.backup_in_progress:
                self.root.after(0, lambda: self.backup_failed_with_options(error_msg))
    
    def update_progress(self, progress, message):
        """Update progress bar and status."""
        self.progress_var.set(progress)
        self.status_label.config(text=message)
        self.log_message(f"Progress: {progress:.1f}% - {message}")
    
    def backup_completed(self, backup_name):
        """Manipular conclusão do backup."""
        self.backup_in_progress = False
        self.backup_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_label.config(text="Backup concluído com sucesso")
        
        self.log_message(f"Backup concluído: {backup_name}")
        messagebox.showinfo("Sucesso", f"Backup concluído com sucesso!\nNome: {backup_name}")
        
        # Resetar campos da interface
        self.reset_backup_fields()
        
        # Atualizar catálogo
        self.refresh_catalog()
        self.refresh_backup_list()
    
    def backup_failed(self, error_message):
        """Manipular falha do backup."""
        self.backup_in_progress = False
        self.backup_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.status_label.config(text="Backup falhou")
        
        self.log_message(f"Backup falhou: {error_message}")
        messagebox.showerror("Backup Falhou", f"Backup falhou: {error_message}")
    
    def backup_failed_with_options(self, error_message):
        """Manipular falha com opções de continuar.""" 
        self.backup_in_progress = False
        self.backup_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.status_label.config(text="Backup falhou")
        
        self.log_message(f"ERRO NO BACKUP: {error_message}")
        
        # Perguntar se quer tentar pular o erro
        result = messagebox.askyesnocancel(
            "Erro no Backup", 
            f"Erro encontrado: {error_message}\n\n"
            "Deseja:\n"
            "• SIM - Tentar pular arquivos com problema\n" 
            "• NÃO - Parar o backup\n"
            "• CANCELAR - Ver detalhes no log"
        )
        
        if result is True:
            # Tentar novamente pulando erros
            self.log_message("Usuário escolheu pular arquivos com problema")
            # Aqui poderia implementar lógica para pular arquivos problemáticos
        elif result is False:
            self.log_message("Usuário escolheu parar o backup")
        else:
            self.log_message("Usuário escolheu verificar detalhes no log")
    
    def reset_backup_fields(self):
        """Resetar campos após backup completo."""
        # Limpar lista de pastas
        self.source_folders.clear()
        self.source_listbox.delete(0, tk.END)
        
        # Limpar título do backup
        self.backup_title_var.set("")
        
        # Resetar progresso
        self.progress_var.set(0)
        self.status_label.config(text="Pronto para novo backup")
        
        self.log_message("Campos resetados para novo backup")
    
    def cancel_backup(self):
        """Cancel the backup process."""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja cancelar o backup?"):
            self.backup_in_progress = False
            self.backup_manager.cancel_backup()
            
            # Close calculation modal if open
            if hasattr(self, 'calculation_modal'):
                self.calculation_modal.close()
                delattr(self, 'calculation_modal')
            
            self.backup_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.status_label.config(text="Backup cancelado")
            self.log_message("Backup cancelado pelo usuário")
    
    def refresh_backup_list(self):
        """Refresh the list of available backups."""
        self.backup_listbox.delete(0, tk.END)
        backups = self.catalog_manager.get_backup_list()
        
        for backup in backups:
            display_text = f"{backup['name']} - {backup['date']} ({format_size(backup['size'])})"
            self.backup_listbox.insert(tk.END, display_text)
    
    def on_backup_selected(self, event):
        """Handle backup selection in restore tab."""
        selection = self.backup_listbox.curselection()
        if selection:
            index = selection[0]
            backups = self.catalog_manager.get_backup_list()
            if index < len(backups):
                backup = backups[index]
                self.load_backup_files(backup)
    
    def load_backup_files(self, backup_info):
        """Load files from selected backup."""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            files = self.restore_manager.get_backup_contents(backup_info['path'])
            self.populate_file_tree(files)
        except Exception as e:
            self.log_message(f"Error loading backup contents: {str(e)}")
            messagebox.showerror("Error", f"Failed to load backup contents: {str(e)}")
    
    def populate_file_tree(self, files):
        """Populate the file tree with backup contents."""
        for file_info in files:
            self.file_tree.insert('', tk.END, 
                                text=file_info['name'],
                                values=(format_size(file_info['size']), 
                                       format_time(file_info['modified'])))
    
    def browse_restore_destination(self):
        """Browse for restore destination."""
        folder = filedialog.askdirectory(title="Select restore destination")
        if folder:
            self.restore_dest_var.set(folder)
    
    def restore_selected(self):
        """Restore selected files."""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select files to restore.")
            return
        
        if not self.restore_dest_var.get():
            messagebox.showerror("Error", "Please select a restore destination.")
            return
        
        self.perform_restore(selected_items)
    
    def restore_all(self):
        """Restore all files from backup."""
        if not self.restore_dest_var.get():
            messagebox.showerror("Error", "Please select a restore destination.")
            return
        
        all_items = self.file_tree.get_children()
        self.perform_restore(all_items)
    
    def perform_restore(self, items):
        """Perform the restore operation."""
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a backup first.")
            return
        
        try:
            index = selection[0]
            backups = self.catalog_manager.get_backup_list()
            backup = backups[index]
            
            # Get selected file names
            file_names = [self.file_tree.item(item)['text'] for item in items]
            
            # Perform restore
            self.restore_manager.restore_files(
                backup['path'],
                file_names,
                self.restore_dest_var.get()
            )
            
            self.log_message(f"Restored {len(file_names)} files to {self.restore_dest_var.get()}")
            messagebox.showinfo("Success", f"Successfully restored {len(file_names)} files.")
            
        except Exception as e:
            error_msg = f"Restore failed: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Restore Failed", error_msg)
    
    def refresh_catalog(self):
        """Refresh the backup catalog display."""
        # Clear existing items
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        
        # Load catalog entries
        catalog_entries = self.catalog_manager.get_catalog_entries()
        
        for entry in catalog_entries:
            self.catalog_tree.insert('', tk.END,
                                   text=entry['name'],
                                   values=(entry['date'],
                                          format_size(entry['size']),
                                          entry['file_count'],
                                          entry['location']))
    
    def delete_catalog_entry(self):
        """Delete selected catalog entry."""
        selected_items = self.catalog_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a catalog entry to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected catalog entries?"):
            for item in selected_items:
                backup_name = self.catalog_tree.item(item)['text']
                try:
                    self.catalog_manager.delete_catalog_entry(backup_name)
                    self.log_message(f"Deleted catalog entry: {backup_name}")
                except Exception as e:
                    self.log_message(f"Error deleting catalog entry {backup_name}: {str(e)}")
            
            self.refresh_catalog()
            self.refresh_backup_list()
    
    def export_catalog(self):
        """Export catalog to file."""
        filename = filedialog.asksaveasfilename(
            title="Export Catalog",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.catalog_manager.export_catalog(filename)
                self.log_message(f"Catalog exported to: {filename}")
                messagebox.showinfo("Success", f"Catalog exported successfully to {filename}")
            except Exception as e:
                error_msg = f"Export failed: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("Export Failed", error_msg)
    
    def log_message(self, message):
        """Log a message to the log display."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def load_settings(self):
        """Load application settings."""
        # Initialize with default destination if available
        try:
            self.refresh_catalog()
            self.refresh_backup_list()
        except:
            pass
