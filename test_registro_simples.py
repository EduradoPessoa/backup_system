#!/usr/bin/env python3
"""
Teste simples de registro para diagnosticar o problema
"""

import sys
import os
sys.path.append('.')

def test_registration():
    print("=== TESTE DE REGISTRO DIRETO ===")
    
    # Simular exatamente o que a interface faz
    nome_input = "Eduardo Pessoa"
    email_input = "eduardo@phoenyx.com.br"
    
    # Aplicar .strip() como na interface
    name = nome_input.strip()
    email = email_input.strip()
    
    print(f"Nome original: '{nome_input}'")
    print(f"Nome após strip: '{name}'")
    print(f"Validação if not name: {not name}")
    print(f"Validação len(name) < 2: {len(name) < 2}")
    
    # Teste de validação como na interface
    if not name:
        print("ERRO: Nome está vazio")
        return False
        
    if len(name) < 2:
        print("ERRO: Nome muito curto")
        return False
        
    if not email:
        print("ERRO: Email está vazio")
        return False
    
    print("✓ Validações passaram")
    
    # Testar registro no user_manager
    from user_manager import user_manager
    print(f"Tentando registrar: {name} / {email}")
    
    user_id = user_manager.register_user(name, email)
    print(f"Resultado: {user_id}")
    
    if user_id:
        print("✓ Registro bem-sucedido!")
        return True
    else:
        print("✗ Falha no registro")
        return False

if __name__ == "__main__":
    success = test_registration()
    if success:
        print("\n=== RESULTADO: TESTE PASSOU ===")
    else:
        print("\n=== RESULTADO: TESTE FALHOU ===")