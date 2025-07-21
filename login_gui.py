#!/usr/bin/env python3
"""
Interface de Login
Desktop Backup Manager - PHOENYX TECNOLOGIA © 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from user_manager import user_manager

class LoginWindow:
    def __init__(self, on_success_callback=None):
        self.on_success_callback = on_success_callback
        self.root = tk.Tk()
        self.root.title("Desktop Backup Manager - Login - PHOENYX TECNOLOGIA 2025")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        # Centralize window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"450x500+{x}+{y}")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Configurar interface de login."""
        # Configurar estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('TButton', font=('Segoe UI', 10), padding=(15, 8))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        title_label = ttk.Label(main_frame, text="Desktop Backup Manager", 
                               style='Title.TLabel', anchor='center')
        title_label.pack(pady=(0, 10))
        
        # Branding
        branding_label = ttk.Label(main_frame, text="PHOENYX TECNOLOGIA © 2025", 
                                  font=('Segoe UI', 10, 'italic'),
                                  foreground='#666666', anchor='center')
        branding_label.pack(pady=(0, 30))
        
        # Verificar se já existe sessão
        current_user = user_manager.get_current_user()
        if current_user:
            self.show_welcome_back(main_frame, current_user)
        else:
            self.show_login_form(main_frame)
    
    def show_welcome_back(self, parent, user):
        """Mostrar tela de boas-vindas para usuário logado."""
        welcome_frame = ttk.LabelFrame(parent, text="Bem-vindo de volta!", padding=20)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        user_label = ttk.Label(welcome_frame, text=f"Olá, {user['name']}!", 
                              style='Heading.TLabel')
        user_label.pack(pady=(0, 10))
        
        email_label = ttk.Label(welcome_frame, text=f"Email: {user['email']}")
        email_label.pack(pady=(0, 15))
        
        # Botões
        button_frame = ttk.Frame(welcome_frame)
        button_frame.pack(fill=tk.X)
        
        continue_btn = ttk.Button(button_frame, text="Continuar", 
                                 command=self.continue_logged_in)
        continue_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        logout_btn = ttk.Button(button_frame, text="Trocar Usuário", 
                               command=self.logout_and_show_login)
        logout_btn.pack(side=tk.LEFT)
        
        # Estatísticas
        self.show_user_stats(parent, user)
    
    def show_user_stats(self, parent, user):
        """Mostrar estatísticas do usuário."""
        stats = user_manager.get_user_stats()
        if not stats:
            return
        
        stats_frame = ttk.LabelFrame(parent, text="Suas Estatísticas", padding=20)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Grid de estatísticas
        stats_info = [
            ("Total de Backups:", f"{stats['total_backups']}"),
            ("Tamanho Total:", f"{stats['total_size'] / (1024**3):.1f} GB"),
            ("Membro desde:", stats['member_since'][:10] if stats['member_since'] else "N/A"),
            ("Último acesso:", stats['last_login'][:10] if stats['last_login'] else "Primeiro acesso")
        ]
        
        for i, (label, value) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label, font=('Segoe UI', 9, 'bold')).grid(
                row=i, column=0, sticky='w', pady=2)
            ttk.Label(stats_frame, text=value).grid(
                row=i, column=1, sticky='w', padx=(20, 0), pady=2)
    
    def show_login_form(self, parent):
        """Mostrar formulário de login/registro."""
        # Notebook para Login/Registro
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de Login
        login_frame = ttk.Frame(notebook, padding=20)
        notebook.add(login_frame, text="Entrar")
        
        self.create_login_tab(login_frame)
        
        # Aba de Registro
        register_frame = ttk.Frame(notebook, padding=20)
        notebook.add(register_frame, text="Registrar")
        
        self.create_register_tab(register_frame)
        
        # Informações importantes
        info_frame = ttk.LabelFrame(parent, text="Informações Importantes", padding=15)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = """• Este aplicativo é GRATUITO para uso pessoal
• Seus dados ficam no seu computador
• O registro ajuda a melhorar o aplicativo
• Não compartilhamos seus dados pessoais"""
        
        info_label = ttk.Label(info_frame, text=info_text, font=('Segoe UI', 9))
        info_label.pack()
    
    def create_login_tab(self, parent):
        """Criar aba de login."""
        ttk.Label(parent, text="Entre com seu email:", style='Heading.TLabel').pack(pady=(0, 15))
        
        # Email
        ttk.Label(parent, text="Email:").pack(anchor='w')
        self.login_email_var = tk.StringVar()
        email_entry = ttk.Entry(parent, textvariable=self.login_email_var, width=40, font=('Segoe UI', 11))
        email_entry.pack(fill=tk.X, pady=(5, 15))
        email_entry.focus()
        
        # Botão de login
        login_btn = ttk.Button(parent, text="Entrar", command=self.do_login)
        login_btn.pack(pady=(0, 15))
        
        # Bind Enter key
        email_entry.bind('<Return>', lambda e: self.do_login())
        
        # Informação adicional
        ttk.Label(parent, text="Não possui conta? Use a aba 'Registrar'", 
                 font=('Segoe UI', 9, 'italic')).pack()
    
    def create_register_tab(self, parent):
        """Criar aba de registro."""
        ttk.Label(parent, text="Crie sua conta gratuita:", style='Heading.TLabel').pack(pady=(0, 15))
        
        # Nome
        ttk.Label(parent, text="Nome completo:").pack(anchor='w')
        self.register_name_var = tk.StringVar()
        name_entry = ttk.Entry(parent, textvariable=self.register_name_var, width=40, font=('Segoe UI', 11))
        name_entry.pack(fill=tk.X, pady=(5, 10))
        name_entry.focus()  # Dar foco inicial ao campo nome
        
        # Email
        ttk.Label(parent, text="Email:").pack(anchor='w')
        self.register_email_var = tk.StringVar()
        email_entry = ttk.Entry(parent, textvariable=self.register_email_var, width=40, font=('Segoe UI', 11))
        email_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Botão de registro
        register_btn = ttk.Button(parent, text="Criar Conta Gratuita", command=self.do_register)
        register_btn.pack(pady=(0, 15))
        
        # Bind Enter key para ambos os campos
        name_entry.bind('<Return>', lambda e: self.do_register())
        email_entry.bind('<Return>', lambda e: self.do_register())
        
        # Termos de uso
        terms_text = """Ao criar uma conta, você concorda que:
• Os dados ficam no seu computador
• Podemos coletar estatísticas anônimas de uso
• O aplicativo é fornecido gratuitamente"""
        
        ttk.Label(parent, text=terms_text, font=('Segoe UI', 8, 'italic'), 
                 foreground='#666666').pack()
    
    def validate_email(self, email):
        """Validar formato do email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def do_login(self):
        """Executar login."""
        email = self.login_email_var.get().strip()
        
        if not email:
            messagebox.showerror("Erro", "Por favor, digite seu email.")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Erro", "Por favor, digite um email válido.")
            return
        
        user = user_manager.login_user(email)
        if user:
            user_manager.save_current_session(user)
            messagebox.showinfo("Sucesso", f"Bem-vindo de volta, {user['name']}!")
            self.close_and_continue()
        else:
            messagebox.showerror("Erro", "Email não encontrado. Registre-se primeiro na aba 'Registrar'.")
    
    def do_register(self):
        """Executar registro."""
        name = self.register_name_var.get().strip()
        email = self.register_email_var.get().strip()
        
        # Debug - imprimir valores capturados
        print(f"DEBUG - Nome capturado: '{name}' (len: {len(name)})")
        print(f"DEBUG - Email capturado: '{email}' (len: {len(email)})")
        print(f"DEBUG - Nome original: '{self.register_name_var.get()}'")
        print(f"DEBUG - Validação nome vazio: {not name}")
        print(f"DEBUG - Validação len < 2: {len(name) < 2}")
        
        if not name:
            print("DEBUG - Erro: nome está vazio")
            messagebox.showerror("Erro", "Por favor, digite seu nome.")
            return
        
        if len(name) < 2:
            print("DEBUG - Erro: nome muito curto")
            messagebox.showerror("Erro", "Nome deve ter pelo menos 2 caracteres.")
            return
        
        if not email:
            messagebox.showerror("Erro", "Por favor, digite seu email.")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Erro", "Por favor, digite um email válido.")
            return
        
        user_id = user_manager.register_user(name, email)
        if user_id:
            # Fazer login automático após registro
            user = user_manager.login_user(email)
            if user:
                user_manager.save_current_session(user)
                messagebox.showinfo("Sucesso", f"Conta criada com sucesso!\nBem-vindo, {name}!")
                self.close_and_continue()
        else:
            messagebox.showerror("Erro", "Este email já está em uso. Tente fazer login.")
    
    def logout_and_show_login(self):
        """Fazer logout e mostrar formulário de login."""
        user_manager.logout_user()
        self.root.destroy()
        self.__init__(self.on_success_callback)
        self.run()
    
    def continue_logged_in(self):
        """Continuar com usuário logado."""
        user = user_manager.get_current_user()
        user_manager.log_user_action('app_start')
        self.close_and_continue()
    
    def close_and_continue(self):
        """Fechar janela e continuar."""
        self.root.destroy()
        if self.on_success_callback:
            self.on_success_callback()
    
    def run(self):
        """Executar janela de login."""
        self.root.mainloop()

def show_login_window(on_success_callback=None):
    """Mostrar janela de login."""
    login_window = LoginWindow(on_success_callback)
    login_window.run()

if __name__ == "__main__":
    show_login_window()