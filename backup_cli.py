#!/usr/bin/env python3
"""
Desktop Backup Manager - Command Line Interface
Permite executar backups via linha de comando, ideal para automação e agendamento.
"""

import sys
import os
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backup_manager import BackupManager
from catalog_manager import CatalogManager
from restore_manager import RestoreManager
from utils import format_size, format_time

class BackupCLI:
    def __init__(self):
        self.backup_manager = BackupManager()
        self.catalog_manager = CatalogManager()
        self.restore_manager = RestoreManager()
    
    def create_backup(self, args):
        """Criar um novo backup."""
        try:
            # Validar pastas de origem
            source_folders = []
            for folder in args.source:
                if os.path.exists(folder) and os.path.isdir(folder):
                    source_folders.append(os.path.abspath(folder))
                    print(f"✓ Pasta de origem adicionada: {folder}")
                else:
                    print(f"✗ Pasta não encontrada: {folder}")
                    return False
            
            if not source_folders:
                print("Erro: Nenhuma pasta de origem válida encontrada.")
                return False
            
            # Validar destino
            if not os.path.exists(args.destination):
                print(f"Erro: Pasta de destino não existe: {args.destination}")
                return False
            
            # Função de progresso
            def progress_callback(current, total, message):
                if args.verbose:
                    progress = (current / total) * 100 if total > 0 else 0
                    print(f"\r[{progress:5.1f}%] {message}", end="", flush=True)
            
            print(f"\nIniciando backup: {args.title}")
            print(f"Origem: {', '.join(source_folders)}")
            print(f"Destino: {args.destination}")
            print(f"Compactação: {args.compression}")
            print(f"Incluir subpastas: {'Sim' if args.include_subdirs else 'Não'}")
            print("-" * 60)
            
            # Executar backup
            backup_name = self.backup_manager.create_backup(
                source_folders,
                args.destination,
                args.compression,
                args.include_subdirs,
                progress_callback if args.verbose else None,
                args.title
            )
            
            if backup_name:
                if args.verbose:
                    print()  # Nova linha após progresso
                print(f"✓ Backup criado com sucesso: {backup_name}")
                
                # Obter informações do backup
                backup_info = self.catalog_manager.get_backup_info(backup_name)
                if backup_info:
                    print(f"  Arquivo: {backup_info['filename']}")
                    print(f"  Tamanho: {format_size(backup_info['size'])}")
                    print(f"  Arquivos: {backup_info['file_count']}")
                
                return True
            else:
                print("✗ Falha ao criar backup")
                return False
                
        except KeyboardInterrupt:
            print("\n\nBackup cancelado pelo usuário.")
            return False
        except Exception as e:
            print(f"\nErro durante backup: {str(e)}")
            return False
    
    def list_backups(self, args):
        """Listar backups disponíveis."""
        try:
            backups = self.catalog_manager.get_catalog_entries()
            
            if not backups:
                print("Nenhum backup encontrado no catálogo.")
                return True
            
            print(f"{'Nome':<30} {'Data':<20} {'Tamanho':<12} {'Arquivos':<8}")
            print("-" * 75)
            
            for backup in backups:
                date_str = format_time(backup['date'])
                size_str = format_size(backup['size'])
                files_str = str(backup.get('file_count', 0))
                
                print(f"{backup['name']:<30} {date_str:<20} {size_str:<12} {files_str:<8}")
                
                if args.verbose:
                    print(f"  Local: {backup['path']}")
                    print(f"  Pastas: {', '.join(backup.get('source_folders', []))}")
                    print()
            
            return True
            
        except Exception as e:
            print(f"Erro ao listar backups: {str(e)}")
            return False
    
    def restore_backup(self, args):
        """Restaurar arquivos de um backup."""
        try:
            # Encontrar backup
            backup_info = self.catalog_manager.get_backup_info(args.backup_name)
            if not backup_info:
                print(f"Backup não encontrado: {args.backup_name}")
                return False
            
            # Validar destino
            if not os.path.exists(args.destination):
                print(f"Pasta de destino não existe: {args.destination}")
                return False
            
            print(f"Restaurando backup: {args.backup_name}")
            print(f"De: {backup_info['path']}")
            print(f"Para: {args.destination}")
            print("-" * 60)
            
            # Executar restauração
            if args.files:
                # Restaurar arquivos específicos
                self.restore_manager.restore_files(
                    backup_info['path'],
                    args.files,
                    args.destination
                )
                print(f"✓ {len(args.files)} arquivo(s) restaurado(s) com sucesso")
            else:
                # Restaurar todos os arquivos
                contents = self.restore_manager.get_backup_contents(backup_info['path'])
                file_names = [f['name'] for f in contents]
                
                self.restore_manager.restore_files(
                    backup_info['path'],
                    file_names,
                    args.destination
                )
                print(f"✓ Todos os arquivos ({len(file_names)}) restaurados com sucesso")
            
            return True
            
        except Exception as e:
            print(f"Erro durante restauração: {str(e)}")
            return False
    
    def show_backup_info(self, args):
        """Mostrar informações detalhadas de um backup."""
        try:
            backup_info = self.catalog_manager.get_backup_info(args.backup_name)
            if not backup_info:
                print(f"Backup não encontrado: {args.backup_name}")
                return False
            
            print(f"Informações do Backup: {args.backup_name}")
            print("=" * 60)
            print(f"Nome do arquivo: {backup_info['filename']}")
            print(f"Data de criação: {format_time(backup_info['date'])}")
            print(f"Tamanho: {format_size(backup_info['size'])}")
            print(f"Tipo de compactação: {backup_info['compression']}")
            print(f"Número de arquivos: {backup_info['file_count']}")
            print(f"Local: {backup_info['path']}")
            print(f"Pastas de origem:")
            for folder in backup_info.get('source_folders', []):
                print(f"  - {folder}")
            
            if args.list_files:
                print(f"\nArquivos no backup:")
                contents = self.restore_manager.get_backup_contents(backup_info['path'])
                for file_info in contents:
                    print(f"  - {file_info['name']} ({format_size(file_info['size'])})")
            
            return True
            
        except Exception as e:
            print(f"Erro ao obter informações: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Desktop Backup Manager - Interface de Linha de Comando",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Criar backup
  python backup_cli.py backup --title "Documentos_2025" --source "C:\\Users\\User\\Documents" --destination "D:\\Backups"
  
  # Criar backup com múltiplas pastas
  python backup_cli.py backup --title "Backup_Completo" --source "C:\\Users\\User\\Documents" "C:\\Users\\User\\Pictures" --destination "D:\\Backups" --compression tar.gz
  
  # Listar backups
  python backup_cli.py list
  
  # Mostrar informações de um backup
  python backup_cli.py info "Documentos_2025_20250121_143000"
  
  # Restaurar backup completo
  python backup_cli.py restore "Documentos_2025_20250121_143000" --destination "C:\\Restore"
  
  # Restaurar arquivos específicos
  python backup_cli.py restore "Documentos_2025_20250121_143000" --destination "C:\\Restore" --files "documento.txt" "planilha.xlsx"

Para agendamento no Windows:
  schtasks /create /tn "Backup Diário" /tr "python C:\\caminho\\backup_cli.py backup --title Backup_Diario --source C:\\Users\\User\\Documents --destination D:\\Backups" /sc daily /st 02:00
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Criar um novo backup')
    backup_parser.add_argument('--title', required=True, help='Título do backup (ex: Documentos_2025)')
    backup_parser.add_argument('--source', nargs='+', required=True, help='Pasta(s) de origem para backup')
    backup_parser.add_argument('--destination', required=True, help='Pasta de destino')
    backup_parser.add_argument('--compression', choices=['zip', 'tar.gz'], default='zip', help='Tipo de compactação (padrão: zip)')
    backup_parser.add_argument('--no-subdirs', action='store_true', help='Não incluir subpastas')
    backup_parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar progresso detalhado')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar backups disponíveis')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar informações detalhadas')
    
    # Comando info
    info_parser = subparsers.add_parser('info', help='Mostrar informações de um backup')
    info_parser.add_argument('backup_name', help='Nome do backup')
    info_parser.add_argument('--list-files', action='store_true', help='Listar arquivos no backup')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar arquivos de um backup')
    restore_parser.add_argument('backup_name', help='Nome do backup')
    restore_parser.add_argument('--destination', required=True, help='Pasta de destino para restauração')
    restore_parser.add_argument('--files', nargs='+', help='Arquivos específicos para restaurar (opcional)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Configurar argumentos processados
    if hasattr(args, 'no_subdirs'):
        args.include_subdirs = not args.no_subdirs
    
    cli = BackupCLI()
    
    # Executar comando
    success = False
    if args.command == 'backup':
        success = cli.create_backup(args)
    elif args.command == 'list':
        success = cli.list_backups(args)
    elif args.command == 'info':
        success = cli.show_backup_info(args)
    elif args.command == 'restore':
        success = cli.restore_backup(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())