"""
Modal de progresso separado para análise de espaço.
"""
import tkinter as tk
from tkinter import ttk
import threading

class ProgressModal:
    def __init__(self, parent, title="Analisando espaço..."):
        self.parent = parent
        self.modal = tk.Toplevel(parent)
        self.modal.title(title)
        self.modal.geometry("400x150")
        self.modal.resizable(False, False)
        self.modal.transient(parent)
        self.modal.grab_set()
        
        # Centralizar na tela parent
        self.modal.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._center_modal()
        
        # Variáveis de progresso
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Iniciando análise...")
        self.cancelled = False
        
        self._create_widgets()
    
    def _center_modal(self):
        """Centralizar modal na janela pai."""
        self.modal.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        modal_width = self.modal.winfo_width()
        modal_height = self.modal.winfo_height()
        
        x = parent_x + (parent_width // 2) - (modal_width // 2)
        y = parent_y + (parent_height // 2) - (modal_height // 2)
        
        self.modal.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Criar widgets do modal."""
        # Frame principal
        main_frame = ttk.Frame(self.modal, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=('Segoe UI', 10))
        status_label.pack(pady=(0, 10))
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           variable=self.progress_var, 
                                           maximum=100, 
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Label de progresso em %
        self.percent_label = ttk.Label(main_frame, text="0%", 
                                      font=('Segoe UI', 9))
        self.percent_label.pack()
        
        # Botão cancelar
        cancel_btn = ttk.Button(main_frame, text="Cancelar", 
                               command=self.cancel)
        cancel_btn.pack(pady=(10, 0))
        
    def update_progress(self, progress, status_text):
        """Atualizar progresso do modal."""
        if self.modal.winfo_exists():
            self.progress_var.set(progress)
            self.status_var.set(status_text)
            self.percent_label.config(text=f"{progress:.0f}%")
            self.modal.update_idletasks()
    
    def cancel(self):
        """Cancelar operação."""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Fechar modal."""
        if self.modal.winfo_exists():
            self.modal.destroy()
    
    def on_closing(self):
        """Tentar fechar modal."""
        self.cancel()
    
    def is_cancelled(self):
        """Verificar se foi cancelado."""
        return self.cancelled