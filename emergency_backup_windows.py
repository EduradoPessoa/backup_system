#!/usr/bin/env python3
"""
Backup de Emergência para Windows
Versão simplificada sem sistema de login
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
from pathlib import Path
from datetime import datetime

class EmergencyBackup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PHOENYX BACKUP - Modo Emergência")
        self.root.geometry("600x400")
        
        # Configurar interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface."""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="PHOENYX BACKUP - MODO EMERGÊNCIA", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        info_label = ttk.Label(main_frame, text="Versão simplificada sem login para uso imediato",
                              font=('Arial', 10))
        info_label.pack(pady=(0, 20))
        
        # Seleção de pasta
        ttk.Label(main_frame, text="Pasta para backup:", font=('Arial', 12)).pack(anchor='w')
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(5, 20))
        
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        folder_btn = ttk.Button(folder_frame, text="Selecionar", command=self.select_folder)
        folder_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Destino
        ttk.Label(main_frame, text="Destino do backup:", font=('Arial', 12)).pack(anchor='w')
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=(5, 20))
        
        self.dest_var = tk.StringVar(value=str(Path.home() / "backup_emergencia"))
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, width=50)
        dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        dest_btn = ttk.Button(dest_frame, text="Selecionar", command=self.select_destination)
        dest_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Pronto para backup")
        ttk.Label(main_frame, textvariable=self.progress_var).pack(pady=(20, 5))
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        backup_btn = ttk.Button(button_frame, text="FAZER BACKUP", command=self.do_backup)
        backup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Sair", command=self.root.quit).pack(side=tk.RIGHT)
    
    def select_folder(self):
        """Selecionar pasta para backup."""
        folder = filedialog.askdirectory(title="Selecione a pasta para backup")
        if folder:
            self.folder_var.set(folder)
    
    def select_destination(self):
        """Selecionar destino do backup."""
        dest = filedialog.askdirectory(title="Selecione o destino do backup")
        if dest:
            self.dest_var.set(dest)
    
    def do_backup(self):
        """Fazer backup."""
        source = self.folder_var.get()
        dest_dir = self.dest_var.get()
        
        if not source:
            messagebox.showerror("Erro", "Selecione uma pasta para backup!")
            return
        
        if not os.path.exists(source):
            messagebox.showerror("Erro", "Pasta de origem não existe!")
            return
        
        try:
            # Criar diretório de destino
            os.makedirs(dest_dir, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = os.path.basename(source)
            backup_name = f"backup_{folder_name}_{timestamp}.zip"
            backup_path = os.path.join(dest_dir, backup_name)
            
            self.progress_var.set("Criando backup...")
            self.progress.start()
            self.root.update()
            
            # Criar backup
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, source)
                        zipf.write(file_path, arc_path)
            
            self.progress.stop()
            self.progress_var.set("Backup concluído!")
            
            size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
            messagebox.showinfo("Sucesso", 
                               f"Backup criado com sucesso!\n\n"
                               f"Arquivo: {backup_name}\n"
                               f"Tamanho: {size:.2f} MB\n"
                               f"Local: {dest_dir}")
            
        except Exception as e:
            self.progress.stop()
            self.progress_var.set("Erro no backup")
            messagebox.showerror("Erro", f"Erro ao criar backup:\n{str(e)}")
    
    def run(self):
        """Executar aplicativo."""
        self.root.mainloop()

if __name__ == "__main__":
    print("=== PHOENYX BACKUP - MODO EMERGÊNCIA ===")
    print("Versão sem login para uso imediato no Windows")
    print("Para usar o sistema completo, resolva o problema de login primeiro")
    print("")
    
    app = EmergencyBackup()
    app.run()