#!/usr/bin/env python3
"""
Script de teste para diagnosticar problema de registro
"""

import sys
sys.path.append('.')

from login_gui import LoginWindow
import tkinter as tk

def main():
    print("=== TESTE DE REGISTRO ===")
    print("Abrindo interface de login...")
    
    def on_success():
        print("✓ Login/registro bem-sucedido!")
        
    try:
        app = LoginWindow(on_success)
        print("Interface criada. Execute os testes manualmente:")
        print("1. Vá para aba 'Registrar'")
        print("2. Digite nome: 'João Silva'")
        print("3. Digite email: 'joao@teste.com'")
        print("4. Clique em 'Criar Conta Gratuita'")
        print("5. Observe mensagens de DEBUG no console")
        app.run()
    except Exception as e:
        print(f"Erro ao abrir interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()