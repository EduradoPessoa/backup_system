#!/usr/bin/env python3
"""
Script para criar executáveis do Desktop Backup Manager
PHOENYX TECNOLOGIA © 2025
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_platform_info():
    """Get platform-specific information."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        extension = ".exe"
        separator = ";"
    else:
        extension = ""
        separator = ":"
    
    return system, arch, extension, separator

def create_spec_file():
    """Create PyInstaller spec file for better control."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'zipfile',
        'tarfile',
        'json',
        'pathlib',
        'datetime',
        'os',
        'shutil',
        'argparse',
        'flask',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesktopBackupManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False para GUI, True para console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione um ícone .ico aqui se desejar
)
'''
    
    with open('backup_manager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ Arquivo .spec criado")

def build_executable():
    """Build the executable using PyInstaller."""
    system, arch, extension, separator = get_platform_info()
    
    print(f"🖥️  Criando executável para {system.title()} ({arch})")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("dist") / f"{system}_{arch}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create spec file for better control
    create_spec_file()
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        f"--distpath={output_dir}",
        "backup_manager.spec"
    ]
    
    print(f"🔨 Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Build concluído com sucesso!")
        
        # Copy additional files
        copy_additional_files(output_dir)
        
        # Create readme
        create_readme(output_dir, system)
        
        print(f"📦 Executável criado em: {output_dir}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante o build:")
        print(f"Código de saída: {e.returncode}")
        print(f"Stderr: {e.stderr}")
        return False

def copy_additional_files(output_dir):
    """Copy additional files to distribution."""
    files_to_copy = [
        "README.md",
        "backup_cli.py",
    ]
    
    exe_dir = output_dir / "DesktopBackupManager"
    
    # Ensure exe_dir exists
    if not exe_dir.exists():
        print(f"⚠️  Diretório não encontrado: {exe_dir}")
        return
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            try:
                dest = exe_dir / file_name
                shutil.copy2(file_name, dest)
                print(f"✓ Copiado: {file_name}")
            except Exception as e:
                print(f"⚠️  Erro ao copiar {file_name}: {e}")

def create_readme(output_dir, system):
    """Create a README for the executable."""
    exe_dir = output_dir / "DesktopBackupManager"
    readme_path = exe_dir / "LEIA-ME.txt"
    
    content = f"""Desktop Backup Manager
PHOENYX TECNOLOGIA © 2025

=== INSTRUÇÕES DE USO ===

1. INTERFACE GRÁFICA:
   - Execute: DesktopBackupManager{'.exe' if system == 'windows' else ''}
   - Interface completa com todas as funcionalidades

2. LINHA DE COMANDO:
   - Execute: python backup_cli.py --help
   - Para automação e agendamento de tarefas

=== FUNCIONALIDADES ===

✓ Backup de múltiplas pastas
✓ Compressão ZIP e TAR.GZ
✓ Catálogo de backups
✓ Restauração seletiva
✓ Interface em português
✓ Títulos personalizados para backups
✓ Tratamento de arquivos abertos/bloqueados
✓ Linha de comando para automação

=== REQUISITOS ===

{system.title()}: Não há dependências adicionais.
O executável é standalone e pode ser executado diretamente.

=== SUPORTE ===

Para suporte técnico, entre em contato com:
PHOENYX TECNOLOGIA
Email: [seu-email@phoenyx.com]

Versão: 1.0.0
Data: Janeiro 2025
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ README criado: {readme_path}")

def create_build_script():
    """Create platform-specific build scripts."""
    system, arch, extension, separator = get_platform_info()
    
    if system == "windows":
        script_content = f"""@echo off
echo Criando executavel para Windows...
python build_executable.py
echo.
echo Executavel criado em dist\\windows_{arch}\\
pause
"""
        script_name = "build_windows.bat"
    else:
        script_content = f"""#!/bin/bash
echo "Criando executável para {system.title()}..."
python3 build_executable.py
echo
echo "Executável criado em dist/{system}_{arch}/"
read -p "Pressione Enter para continuar..."
"""
        script_name = f"build_{system}.sh"
    
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if system != "windows":
        os.chmod(script_name, 0o755)
    
    print(f"✓ Script de build criado: {script_name}")

def main():
    """Main function."""
    print("=" * 60)
    print("   DESKTOP BACKUP MANAGER - GERADOR DE EXECUTÁVEIS")
    print("              PHOENYX TECNOLOGIA © 2025")
    print("=" * 60)
    
    system, arch, extension, separator = get_platform_info()
    
    print(f"Sistema detectado: {system.title()} ({arch})")
    print()
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado!")
        print("Instale com: pip install pyinstaller")
        return False
    
    # Create build scripts
    create_build_script()
    
    # Build executable
    success = build_executable()
    
    if success:
        print()
        print("=" * 60)
        print("🎉 EXECUTÁVEL CRIADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Teste o executável na pasta dist/")
        print("2. Para outros sistemas operacionais:")
        print("   - Linux: Execute build_linux.sh")
        print("   - macOS: Execute build_darwin.sh")
        print("   - Windows: Execute build_windows.bat")
        print()
        print("📦 DISTRIBUIÇÃO:")
        print("- Compacte a pasta dist/ para distribuição")
        print("- O executável é standalone (não precisa Python instalado)")
        
    else:
        print()
        print("❌ Falha na criação do executável")
        print("Verifique os erros acima e tente novamente")
    
    return success

if __name__ == "__main__":
    main()