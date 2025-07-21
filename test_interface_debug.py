#!/usr/bin/env python3
"""
Teste específico da interface para debugar problema de registro
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
sys.path.append('.')

def test_interface_values():
    """Testar captura de valores da interface de forma isolada."""
    
    def on_button_click():
        name = name_var.get().strip()
        email = email_var.get().strip()
        
        print(f"=== VALORES CAPTURADOS ===")
        print(f"Nome original: '{name_var.get()}'")
        print(f"Nome após strip: '{name}'")
        print(f"Email original: '{email_var.get()}'")
        print(f"Email após strip: '{email}'")
        print(f"Validação nome vazio: {not name}")
        print(f"Validação nome < 2: {len(name) < 2}")
        
        if not name:
            messagebox.showerror("Erro", "Por favor, digite seu nome.")
            return
        
        if len(name) < 2:
            messagebox.showerror("Erro", "Nome deve ter pelo menos 2 caracteres.")
            return
            
        if not email:
            messagebox.showerror("Erro", "Por favor, digite seu email.")
            return
            
        messagebox.showinfo("Sucesso", f"Valores capturados:\nNome: {name}\nEmail: {email}")
        root.quit()
    
    root = tk.Tk()
    root.title("Teste Interface Debug")
    root.geometry("400x300")
    
    # Configurar interface similar à original
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Teste de Registro", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
    
    # Nome
    ttk.Label(main_frame, text="Nome completo:").pack(anchor='w')
    name_var = tk.StringVar()
    name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40, font=('Segoe UI', 11))
    name_entry.pack(fill=tk.X, pady=(5, 10))
    name_entry.focus()
    
    # Email
    ttk.Label(main_frame, text="Email:").pack(anchor='w')
    email_var = tk.StringVar()
    email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40, font=('Segoe UI', 11))
    email_entry.pack(fill=tk.X, pady=(5, 15))
    
    # Botão
    test_btn = ttk.Button(main_frame, text="Testar Valores", command=on_button_click)
    test_btn.pack(pady=10)
    
    # Instruções
    ttk.Label(main_frame, text="Digite nome e email, depois clique no botão", 
             font=('Segoe UI', 9, 'italic')).pack(pady=10)
    
    # Bind Enter
    name_entry.bind('<Return>', lambda e: on_button_click())
    email_entry.bind('<Return>', lambda e: on_button_click())
    
    print("Interface de teste aberta. Digite valores e teste...")
    root.mainloop()

if __name__ == "__main__":
    test_interface_values()