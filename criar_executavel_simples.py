#!/usr/bin/env python3
"""
Script simplificado para criar executáveis
PHOENYX TECNOLOGIA © 2025
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_simple_executable():
    """Criar executável com comando simples do PyInstaller."""
    print("=" * 60)
    print("   DESKTOP BACKUP MANAGER - CRIADOR EXECUTÁVEL")
    print("              PHOENYX TECNOLOGIA © 2025")
    print("=" * 60)
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("❌ Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller instalado")
    
    # Criar diretório de saída
    output_dir = Path("executaveis")
    output_dir.mkdir(exist_ok=True)
    
    # Comando PyInstaller simplificado
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",              # Um único arquivo
        "--windowed",             # Sem console (GUI)
        "--add-data", "templates:templates",  # Incluir templates
        "--name", "DesktopBackupManager",
        "--distpath", str(output_dir),
        "main.py"
    ]
    
    print(f"🔨 Executando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Executável criado com sucesso!")
            
            # Listar arquivos criados
            exe_files = list(output_dir.glob("DesktopBackupManager*"))
            if exe_files:
                exe_file = exe_files[0]
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"📦 Arquivo: {exe_file}")
                print(f"📏 Tamanho: {size_mb:.1f} MB")
                
                # Criar pacote de distribuição
                create_distribution_package(exe_file)
                
                return True
            else:
                print("❌ Arquivo executável não encontrado")
                return False
        else:
            print(f"❌ Erro no PyInstaller:")
            print(f"Código: {result.returncode}")
            print(f"Erro: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout - PyInstaller demorou muito")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_distribution_package(exe_file):
    """Criar pacote completo para distribuição."""
    package_dir = exe_file.parent / "DesktopBackupManager_Distribuicao"
    package_dir.mkdir(exist_ok=True)
    
    # Copiar executável
    shutil.copy2(exe_file, package_dir)
    
    # Copiar arquivos auxiliares
    files_to_copy = [
        ("backup_cli.py", "Interface de linha de comando"),
        ("README.md", "Documentação"),
        ("GUIA_EXECUTAVEIS.md", "Guia de criação de executáveis"),
    ]
    
    for file_name, description in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, package_dir)
            print(f"✓ Incluído: {file_name}")
    
    # Criar arquivo LEIA-ME
    readme_content = f"""DESKTOP BACKUP MANAGER
PHOENYX TECNOLOGIA © 2025

=== COMO USAR ===

1. INTERFACE GRÁFICA:
   Execute: DesktopBackupManager{'.exe' if sys.platform == 'win32' else ''}
   
2. LINHA DE COMANDO:
   Execute: python backup_cli.py --help

=== FUNCIONALIDADES ===

✓ Backup de múltiplas pastas
✓ Compressão ZIP e TAR.GZ  
✓ Catálogo de backups
✓ Restauração seletiva
✓ Interface em português
✓ Tratamento de arquivos abertos
✓ Automação via linha de comando

=== REQUISITOS ===

Este executável é standalone - não precisa do Python instalado.
Funciona em qualquer computador com o mesmo sistema operacional.

=== SUPORTE ===

PHOENYX TECNOLOGIA
Email: suporte@phoenyx.com.br
Site: www.phoenyx.com.br

Versão: 1.0.0
Data: Janeiro 2025
"""
    
    readme_path = package_dir / "LEIA-ME.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📦 Pacote criado: {package_dir}")
    print(f"📋 Instruções: {readme_path}")

def main():
    """Função principal."""
    success = create_simple_executable()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 EXECUTÁVEL CRIADO COM SUCESSO!")
        print("=" * 60)
        print("\n📁 Localização: pasta 'executaveis/'")
        print("📦 Distribua a pasta 'DesktopBackupManager_Distribuicao'")
        print("\n🔄 Para outros sistemas operacionais:")
        print("- Execute este script no sistema de destino")
        print("- Windows: python criar_executavel_simples.py")
        print("- Linux: python3 criar_executavel_simples.py") 
        print("- macOS: python3 criar_executavel_simples.py")
    else:
        print("\n❌ Falha na criação do executável")
        print("Tente executar manualmente:")
        print("pip install pyinstaller")
        print("pyinstaller --onefile --windowed main.py")

if __name__ == "__main__":
    main()