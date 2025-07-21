#!/usr/bin/env python3
"""
Teste rápido do sistema 7Z
"""
import os
import tempfile
from backup_manager import BackupManager

def teste_7z():
    print("=== TESTE DE COMPRESSÃO 7Z ===")
    
    # Verificar se py7zr está disponível
    try:
        import py7zr
        print(f"✅ py7zr v{py7zr.__version__} disponível")
    except ImportError:
        print("❌ py7zr não encontrado")
        return False
    
    # Criar arquivos de teste
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = os.path.join(temp_dir, "test_source")
        os.makedirs(test_folder)
        
        # Criar alguns arquivos de teste
        for i in range(3):
            with open(os.path.join(test_folder, f"teste_{i}.txt"), "w") as f:
                f.write(f"Conteúdo do arquivo de teste {i}\n" * 100)
        
        # Testar backup 7Z
        backup_manager = BackupManager()
        backup_dest = temp_dir
        
        try:
            resultado = backup_manager.create_backup(
                source_folders=[test_folder],
                destination_path=backup_dest,
                compression_type="7z",
                backup_title="Teste_7Z"
            )
            
            if resultado:
                # Listar arquivos criados no diretório 
                files = [f for f in os.listdir(backup_dest) if f.endswith('.7z')]
                if files:
                    backup_file = files[0]
                    backup_path = os.path.join(backup_dest, backup_file)
                    size = os.path.getsize(backup_path)
                    print(f"✅ Backup 7Z criado: {backup_file} ({size} bytes)")
                    return True
                else:
                    print(f"❌ Nenhum arquivo 7Z encontrado em: {backup_dest}")
                    print(f"Arquivos encontrados: {os.listdir(backup_dest)}")
            else:
                print("❌ Backup falhou")
                
        except Exception as e:
            print(f"❌ Erro no backup 7Z: {e}")
            return False
    
    return False

if __name__ == "__main__":
    sucesso = teste_7z()
    print(f"\n🎯 Resultado: {'SUCESSO' if sucesso else 'FALHA'}")