#!/usr/bin/env python3
"""
Web-based Desktop Backup Application
A web interface for the backup application that works better in Replit environment.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
from datetime import datetime
import threading
from pathlib import Path
import zipfile
import tarfile

from backup_manager import BackupManager
from restore_manager import RestoreManager
from catalog_manager import CatalogManager
from utils import format_size, format_time

app = Flask(__name__)
app.secret_key = 'backup_manager_secret_key'

# Global instances
backup_manager = BackupManager()
restore_manager = RestoreManager()
catalog_manager = CatalogManager()

# Global status for tracking operations
backup_status = {
    'in_progress': False,
    'progress': 0,
    'message': 'Ready',
    'error': None
}

@app.route('/')
def index():
    """Main page with backup interface."""
    return render_template('index.html')

@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Create a new backup."""
    try:
        data = request.get_json()
        source_folders = data.get('source_folders', [])
        destination_path = data.get('destination_path', '')
        compression_type = data.get('compression_type', 'zip')
        include_subdirs = data.get('include_subdirs', True)
        
        if not source_folders:
            return jsonify({'error': 'No source folders selected'}), 400
        
        if not destination_path:
            return jsonify({'error': 'No destination path specified'}), 400
        
        if not os.path.exists(destination_path):
            return jsonify({'error': 'Destination path does not exist'}), 400
        
        # Validate source folders
        valid_folders = []
        for folder in source_folders:
            if os.path.exists(folder) and os.path.isdir(folder):
                valid_folders.append(folder)
        
        if not valid_folders:
            return jsonify({'error': 'No valid source folders found'}), 400
        
        # Start backup in background thread
        backup_thread = threading.Thread(
            target=run_backup_thread,
            args=(valid_folders, destination_path, compression_type, include_subdirs)
        )
        backup_thread.daemon = True
        backup_thread.start()
        
        return jsonify({'message': 'Backup started successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_backup_thread(source_folders, destination_path, compression_type, include_subdirs):
    """Run backup in background thread."""
    global backup_status
    
    def progress_callback(current, total, message):
        backup_status.update({
            'progress': current,
            'message': message
        })
    
    try:
        backup_status.update({
            'in_progress': True,
            'progress': 0,
            'message': 'Starting backup...',
            'error': None
        })
        
        backup_name = backup_manager.create_backup(
            source_folders,
            destination_path,
            compression_type,
            include_subdirs,
            progress_callback
        )
        
        if backup_name:
            backup_status.update({
                'in_progress': False,
                'progress': 100,
                'message': f'Backup completed: {backup_name}',
                'error': None
            })
        else:
            backup_status.update({
                'in_progress': False,
                'progress': 0,
                'message': 'Backup failed',
                'error': 'Backup creation failed'
            })
            
    except Exception as e:
        backup_status.update({
            'in_progress': False,
            'progress': 0,
            'message': 'Backup failed',
            'error': str(e)
        })

@app.route('/api/backup/status')
def backup_status_api():
    """Get current backup status."""
    return jsonify(backup_status)

@app.route('/api/backup/cancel', methods=['POST'])
def cancel_backup():
    """Cancel current backup operation."""
    backup_manager.cancel_backup()
    backup_status.update({
        'in_progress': False,
        'progress': 0,
        'message': 'Backup cancelled',
        'error': None
    })
    return jsonify({'message': 'Backup cancelled'})

@app.route('/api/catalog')
def get_catalog():
    """Get list of all backups in catalog."""
    try:
        entries = catalog_manager.get_catalog_entries()
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/<backup_name>/info')
def get_backup_info(backup_name):
    """Get detailed information about a specific backup."""
    try:
        info = catalog_manager.get_backup_info(backup_name)
        if info:
            return jsonify(info)
        else:
            return jsonify({'error': 'Backup not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/<backup_name>/contents')
def get_backup_contents(backup_name):
    """Get contents of a backup file."""
    try:
        backup_info = catalog_manager.get_backup_info(backup_name)
        if not backup_info:
            return jsonify({'error': 'Backup not found'}), 404
        
        contents = restore_manager.get_backup_contents(backup_info['path'])
        return jsonify(contents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/restore', methods=['POST'])
def restore_files():
    """Restore files from backup."""
    try:
        data = request.get_json()
        backup_name = data.get('backup_name')
        file_names = data.get('file_names', [])
        destination_path = data.get('destination_path')
        preserve_structure = data.get('preserve_structure', True)
        overwrite_existing = data.get('overwrite_existing', False)
        
        if not backup_name:
            return jsonify({'error': 'No backup specified'}), 400
        
        if not destination_path:
            return jsonify({'error': 'No destination path specified'}), 400
        
        backup_info = catalog_manager.get_backup_info(backup_name)
        if not backup_info:
            return jsonify({'error': 'Backup not found'}), 404
        
        result = restore_manager.restore_files(
            backup_info['path'],
            file_names,
            destination_path,
            preserve_structure,
            overwrite_existing
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/folders')
def list_folders():
    """List available folders for selection."""
    try:
        # Start from user's home directory
        home_dir = str(Path.home())
        folders = []
        
        # Add common folders
        common_folders = ['Desktop', 'Documents', 'Downloads', 'Pictures', 'Music', 'Videos']
        for folder in common_folders:
            folder_path = os.path.join(home_dir, folder)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                folders.append({
                    'name': folder,
                    'path': folder_path,
                    'size': format_size(os.path.getsize(folder_path)) if os.path.exists(folder_path) else '0 B'
                })
        
        # Add current directory contents
        current_dir = os.getcwd()
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                folders.append({
                    'name': f"(Current) {item}",
                    'path': item_path,
                    'size': format_size(os.path.getsize(item_path)) if os.path.exists(item_path) else '0 B'
                })
        
        return jsonify(folders)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get backup statistics."""
    try:
        stats = catalog_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory and template file if they don't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Create the HTML template
    template_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Desktop Backup Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #ddd; }
        .tab { padding: 10px 20px; cursor: pointer; border: none; background: none; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #007bff; color: #007bff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .section h3 { margin-top: 0; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }
        .progress-bar { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background-color: #007bff; transition: width 0.3s; }
        .folder-list, .backup-list { max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }
        .folder-item, .backup-item { padding: 5px; cursor: pointer; }
        .folder-item:hover, .backup-item:hover { background-color: #f0f0f0; }
        .folder-item.selected, .backup-item.selected { background-color: #007bff; color: white; }
        .error { color: red; }
        .success { color: green; }
        .log { background-color: #f8f9fa; padding: 10px; height: 200px; overflow-y: auto; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Desktop Backup Manager</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('backup')">Backup</button>
            <button class="tab" onclick="showTab('restore')">Restaurar</button>
            <button class="tab" onclick="showTab('catalog')">Catálogo</button>
            <button class="tab" onclick="showTab('settings')">Configurações</button>
        </div>

        <!-- Backup Tab -->
        <div id="backup" class="tab-content active">
            <div class="section">
                <h3>Pastas de Origem</h3>
                <div class="form-group">
                    <button onclick="loadFolders()">Carregar Pastas Disponíveis</button>
                </div>
                <div id="folder-list" class="folder-list"></div>
                <div class="form-group">
                    <label>Pastas Selecionadas:</label>
                    <div id="selected-folders"></div>
                </div>
            </div>

            <div class="section">
                <h3>Destino</h3>
                <div class="form-group">
                    <label for="destination">Pasta de Destino:</label>
                    <input type="text" id="destination" placeholder="Caminho completo para salvar o backup">
                </div>
            </div>

            <div class="section">
                <h3>Opções</h3>
                <div class="form-group">
                    <label for="compression">Compactação:</label>
                    <select id="compression">
                        <option value="zip">ZIP</option>
                        <option value="tar.gz">TAR.GZ</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="include-subdirs" checked> Incluir subpastas
                    </label>
                </div>
            </div>

            <div class="section">
                <h3>Progresso</h3>
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
                </div>
                <div id="status-message">Pronto</div>
            </div>

            <div class="section">
                <button id="start-backup" onclick="startBackup()">Iniciar Backup</button>
                <button id="cancel-backup" onclick="cancelBackup()" disabled>Cancelar</button>
            </div>
        </div>

        <!-- Restore Tab -->
        <div id="restore" class="tab-content">
            <div class="section">
                <h3>Selecionar Backup</h3>
                <button onclick="loadBackups()">Carregar Backups</button>
                <div id="backup-list" class="backup-list"></div>
            </div>

            <div class="section">
                <h3>Arquivos no Backup</h3>
                <div id="backup-contents"></div>
            </div>

            <div class="section">
                <h3>Destino da Restauração</h3>
                <div class="form-group">
                    <label for="restore-destination">Pasta de Destino:</label>
                    <input type="text" id="restore-destination" placeholder="Onde restaurar os arquivos">
                </div>
            </div>

            <div class="section">
                <button onclick="restoreSelected()">Restaurar Selecionados</button>
                <button onclick="restoreAll()">Restaurar Todos</button>
            </div>
        </div>

        <!-- Catalog Tab -->
        <div id="catalog" class="tab-content">
            <div class="section">
                <h3>Catálogo de Backups</h3>
                <button onclick="loadCatalog()">Atualizar Catálogo</button>
                <div id="catalog-list"></div>
            </div>
        </div>

        <!-- Settings Tab -->
        <div id="settings" class="tab-content">
            <div class="section">
                <h3>Estatísticas</h3>
                <div id="statistics"></div>
            </div>
            
            <div class="section">
                <h3>Log de Operações</h3>
                <div id="log" class="log"></div>
                <button onclick="clearLog()">Limpar Log</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFolders = [];
        let selectedBackup = null;
        let statusInterval = null;

        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        function log(message) {
            const logElement = document.getElementById('log');
            const timestamp = new Date().toLocaleString();
            logElement.innerHTML += `[${timestamp}] ${message}\\n`;
            logElement.scrollTop = logElement.scrollHeight;
        }

        function loadFolders() {
            fetch('/api/folders')
                .then(response => response.json())
                .then(folders => {
                    const folderList = document.getElementById('folder-list');
                    folderList.innerHTML = '';
                    
                    folders.forEach(folder => {
                        const div = document.createElement('div');
                        div.className = 'folder-item';
                        div.innerHTML = `<strong>${folder.name}</strong><br><small>${folder.path} (${folder.size})</small>`;
                        div.onclick = () => selectFolder(folder);
                        folderList.appendChild(div);
                    });
                    
                    log('Pastas carregadas');
                })
                .catch(error => {
                    log(`Erro ao carregar pastas: ${error.message}`);
                });
        }

        function selectFolder(folder) {
            if (!selectedFolders.find(f => f.path === folder.path)) {
                selectedFolders.push(folder);
                updateSelectedFolders();
                log(`Pasta adicionada: ${folder.name}`);
            }
        }

        function updateSelectedFolders() {
            const container = document.getElementById('selected-folders');
            container.innerHTML = '';
            
            selectedFolders.forEach((folder, index) => {
                const div = document.createElement('div');
                div.innerHTML = `${folder.name} <button onclick="removeFolder(${index})">Remover</button>`;
                container.appendChild(div);
            });
        }

        function removeFolder(index) {
            const removed = selectedFolders.splice(index, 1)[0];
            updateSelectedFolders();
            log(`Pasta removida: ${removed.name}`);
        }

        function startBackup() {
            if (selectedFolders.length === 0) {
                alert('Selecione pelo menos uma pasta');
                return;
            }
            
            const destination = document.getElementById('destination').value;
            if (!destination) {
                alert('Especifique um destino');
                return;
            }
            
            const data = {
                source_folders: selectedFolders.map(f => f.path),
                destination_path: destination,
                compression_type: document.getElementById('compression').value,
                include_subdirs: document.getElementById('include-subdirs').checked
            };
            
            fetch('/api/backup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    log(`Erro: ${result.error}`);
                } else {
                    log('Backup iniciado');
                    document.getElementById('start-backup').disabled = true;
                    document.getElementById('cancel-backup').disabled = false;
                    statusInterval = setInterval(checkBackupStatus, 1000);
                }
            })
            .catch(error => {
                log(`Erro ao iniciar backup: ${error.message}`);
            });
        }

        function checkBackupStatus() {
            fetch('/api/backup/status')
                .then(response => response.json())
                .then(status => {
                    document.getElementById('progress-fill').style.width = `${status.progress}%`;
                    document.getElementById('status-message').textContent = status.message;
                    
                    if (!status.in_progress) {
                        clearInterval(statusInterval);
                        document.getElementById('start-backup').disabled = false;
                        document.getElementById('cancel-backup').disabled = true;
                        
                        if (status.error) {
                            log(`Backup falhou: ${status.error}`);
                        } else {
                            log(status.message);
                        }
                    }
                });
        }

        function cancelBackup() {
            fetch('/api/backup/cancel', { method: 'POST' })
                .then(response => response.json())
                .then(result => {
                    log('Backup cancelado');
                    clearInterval(statusInterval);
                    document.getElementById('start-backup').disabled = false;
                    document.getElementById('cancel-backup').disabled = true;
                });
        }

        function loadBackups() {
            fetch('/api/catalog')
                .then(response => response.json())
                .then(backups => {
                    const backupList = document.getElementById('backup-list');
                    backupList.innerHTML = '';
                    
                    backups.forEach(backup => {
                        const div = document.createElement('div');
                        div.className = 'backup-item';
                        div.innerHTML = `<strong>${backup.name}</strong><br><small>${backup.date} - ${backup.size} bytes</small>`;
                        div.onclick = () => selectBackup(backup);
                        backupList.appendChild(div);
                    });
                    
                    log('Backups carregados');
                });
        }

        function selectBackup(backup) {
            selectedBackup = backup;
            document.querySelectorAll('.backup-item').forEach(item => item.classList.remove('selected'));
            event.target.classList.add('selected');
            
            // Load backup contents
            fetch(`/api/backup/${backup.name}/contents`)
                .then(response => response.json())
                .then(contents => {
                    const contentsDiv = document.getElementById('backup-contents');
                    contentsDiv.innerHTML = '<h4>Arquivos:</h4>';
                    
                    contents.forEach(file => {
                        const div = document.createElement('div');
                        div.innerHTML = `${file.name} (${file.size} bytes)`;
                        contentsDiv.appendChild(div);
                    });
                });
        }

        function loadCatalog() {
            fetch('/api/catalog')
                .then(response => response.json())
                .then(backups => {
                    const catalogDiv = document.getElementById('catalog-list');
                    catalogDiv.innerHTML = '';
                    
                    backups.forEach(backup => {
                        const div = document.createElement('div');
                        div.innerHTML = `
                            <h4>${backup.name}</h4>
                            <p>Data: ${backup.date}</p>
                            <p>Tamanho: ${backup.size} bytes</p>
                            <p>Arquivos: ${backup.file_count || 0}</p>
                            <p>Local: ${backup.location}</p>
                            <hr>
                        `;
                        catalogDiv.appendChild(div);
                    });
                    
                    log('Catálogo atualizado');
                });
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        // Load initial data
        window.onload = function() {
            loadFolders();
            loadCatalog();
        };
    </script>
</body>
</html>'''
    
    template_path = templates_dir / 'index.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=False)