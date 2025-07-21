#!/usr/bin/env python3
"""
Open Files Handler
Módulo para lidar com arquivos abertos/bloqueados durante o backup.
"""

import os
import sys
import time
import shutil
import tempfile
import platform
from pathlib import Path

class OpenFilesHandler:
    def __init__(self):
        self.system = platform.system()
        self.retry_attempts = 3
        self.retry_delay = 1  # seconds
        self.skipped_files = []
        self.locked_files = []
        self.copied_files = []
        
    def is_file_locked(self, file_path):
        """
        Verifica se um arquivo está bloqueado/aberto.
        """
        try:
            # Tenta abrir o arquivo para escrita (modo exclusivo)
            with open(file_path, 'r+b') as f:
                pass
            return False
        except (IOError, OSError, PermissionError):
            return True
    
    def get_file_lock_info(self, file_path):
        """
        Obtém informações sobre o bloqueio do arquivo.
        """
        if not self.is_file_locked(file_path):
            return None
            
        lock_info = {
            'file': file_path,
            'reason': 'File is locked or in use',
            'suggestions': []
        }
        
        # Detectar tipos comuns de arquivos problemáticos
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']:
            lock_info['reason'] = 'Microsoft Office document in use'
            lock_info['suggestions'].append('Close Office applications')
            
        elif file_ext in ['.pdf']:
            lock_info['reason'] = 'PDF file might be open in viewer'
            lock_info['suggestions'].append('Close PDF viewers')
            
        elif file_ext in ['.db', '.sqlite', '.mdb']:
            lock_info['reason'] = 'Database file in use'
            lock_info['suggestions'].append('Close database applications')
            
        elif file_ext in ['.log']:
            lock_info['reason'] = 'Log file being written by application'
            lock_info['suggestions'].append('Consider excluding log files')
            
        elif file_ext in ['.tmp', '.temp']:
            lock_info['reason'] = 'Temporary file'
            lock_info['suggestions'].append('Skip temporary files')
            
        return lock_info
    
    def try_backup_file(self, file_path, backup_method, max_retries=None):
        """
        Tenta fazer backup de um arquivo com retry logic.
        
        Args:
            file_path: Caminho do arquivo
            backup_method: Função que executa o backup do arquivo
            max_retries: Número máximo de tentativas
            
        Returns:
            dict: Resultado da operação
        """
        max_retries = max_retries or self.retry_attempts
        
        result = {
            'success': False,
            'file': file_path,
            'method': 'unknown',
            'attempts': 0,
            'error': None,
            'skipped': False
        }
        
        for attempt in range(max_retries + 1):
            result['attempts'] = attempt + 1
            
            try:
                # Tentar método direto primeiro
                if not self.is_file_locked(file_path):
                    backup_method(file_path)
                    result['success'] = True
                    result['method'] = 'direct'
                    self.copied_files.append(file_path)
                    return result
                
                # Se arquivo está bloqueado, tentar métodos alternativos
                if attempt == 0:
                    # Primeira tentativa: aguardar um pouco
                    time.sleep(self.retry_delay)
                    continue
                
                elif attempt == 1:
                    # Segunda tentativa: tentar cópia via shadow copy (Windows)
                    if self.system == "Windows":
                        shadow_result = self._try_shadow_copy(file_path, backup_method)
                        if shadow_result:
                            result['success'] = True
                            result['method'] = 'shadow_copy'
                            self.copied_files.append(file_path)
                            return result
                
                elif attempt == 2:
                    # Terceira tentativa: tentar cópia alternativa
                    alt_result = self._try_alternative_copy(file_path, backup_method)
                    if alt_result:
                        result['success'] = True
                        result['method'] = 'alternative'
                        self.copied_files.append(file_path)
                        return result
                
                # Aguardar antes da próxima tentativa
                if attempt < max_retries:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
            except Exception as e:
                result['error'] = str(e)
                if attempt == max_retries:
                    break
                time.sleep(self.retry_delay)
        
        # Se chegou aqui, não conseguiu fazer backup
        lock_info = self.get_file_lock_info(file_path)
        if lock_info:
            result['lock_info'] = lock_info
            self.locked_files.append(lock_info)
        
        # Decidir se pular ou marcar como erro
        if self._should_skip_file(file_path):
            result['skipped'] = True
            self.skipped_files.append(file_path)
        
        return result
    
    def _try_shadow_copy(self, file_path, backup_method):
        """
        Tenta usar Volume Shadow Copy Service (Windows) para acessar arquivo bloqueado.
        """
        if self.system != "Windows":
            return False
        
        try:
            # Implementação simplificada - em produção usaria APIs do Windows
            # Por enquanto, retorna False (não implementado completamente)
            return False
        except:
            return False
    
    def _try_alternative_copy(self, file_path, backup_method):
        """
        Tenta métodos alternativos de cópia.
        """
        try:
            # Método 1: Tentar cópia para arquivo temporário primeiro
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"backup_temp_{os.path.basename(file_path)}")
            
            try:
                shutil.copy2(file_path, temp_file)
                backup_method(temp_file)
                os.remove(temp_file)
                return True
            except:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
            # Método 2: Tentar leitura em modo compartilhado (Windows)
            if self.system == "Windows":
                try:
                    import msvcrt
                    with open(file_path, 'rb') as src:
                        with open(temp_file, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                    backup_method(temp_file)
                    os.remove(temp_file)
                    return True
                except:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
            
            return False
            
        except Exception:
            return False
    
    def _should_skip_file(self, file_path):
        """
        Determina se um arquivo deve ser pulado baseado em critérios.
        """
        file_ext = Path(file_path).suffix.lower()
        filename = os.path.basename(file_path).lower()
        
        # Pular arquivos temporários óbvios
        skip_extensions = ['.tmp', '.temp', '.log', '.lock', '.swp', '~']
        skip_patterns = ['~$', '.tmp', 'temp']
        
        if file_ext in skip_extensions:
            return True
            
        for pattern in skip_patterns:
            if pattern in filename:
                return True
        
        return False
    
    def get_backup_summary(self):
        """
        Retorna resumo da operação de backup.
        """
        return {
            'total_copied': len(self.copied_files),
            'total_skipped': len(self.skipped_files),
            'total_locked': len(self.locked_files),
            'copied_files': self.copied_files,
            'skipped_files': self.skipped_files,
            'locked_files': self.locked_files
        }
    
    def reset_counters(self):
        """
        Reseta contadores para nova operação.
        """
        self.skipped_files = []
        self.locked_files = []
        self.copied_files = []

def create_backup_report(summary, output_file=None):
    """
    Cria relatório detalhado do backup.
    """
    report_lines = []
    report_lines.append("=== RELATÓRIO DE BACKUP ===")
    report_lines.append(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    report_lines.append("=== RESUMO ===")
    report_lines.append(f"Arquivos copiados: {summary['total_copied']}")
    report_lines.append(f"Arquivos pulados: {summary['total_skipped']}")
    report_lines.append(f"Arquivos bloqueados: {summary['total_locked']}")
    report_lines.append("")
    
    if summary['locked_files']:
        report_lines.append("=== ARQUIVOS BLOQUEADOS ===")
        for lock_info in summary['locked_files']:
            report_lines.append(f"Arquivo: {lock_info['file']}")
            report_lines.append(f"Motivo: {lock_info['reason']}")
            if lock_info['suggestions']:
                report_lines.append("Sugestões:")
                for suggestion in lock_info['suggestions']:
                    report_lines.append(f"  - {suggestion}")
            report_lines.append("")
    
    if summary['skipped_files']:
        report_lines.append("=== ARQUIVOS PULADOS ===")
        for file_path in summary['skipped_files']:
            report_lines.append(f"- {file_path}")
        report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        except Exception as e:
            print(f"Erro ao salvar relatório: {e}")
    
    return report_text