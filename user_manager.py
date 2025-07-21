#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Usuários
Desktop Backup Manager - PHOENYX TECNOLOGIA © 2025
"""

import os
import json
import hashlib
import uuid
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import threading

class UserManager:
    def __init__(self):
        self.db_path = Path.home() / ".backup_manager" / "users.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.api_url = "https://backup-manager-api.phoenyx.com.br"  # URL do seu servidor
        self.local_mode = True  # Modo offline por padrão
        self.init_database()
        
    def init_database(self):
        """Inicializar banco de dados local."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            total_backups INTEGER DEFAULT 0,
            total_size INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )''')
        
        # Tabela de sessões
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Tabela de estatísticas de uso
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action_type TEXT,  -- backup, restore, view_catalog
            details TEXT,      -- JSON com detalhes
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, name, email):
        """Registrar novo usuário."""
        try:
            user_id = str(uuid.uuid4())
            
            # Tentar registrar online primeiro
            if self.try_online_register(user_id, name, email):
                return self.save_user_local(user_id, name, email)
            
            # Fallback para registro local
            return self.save_user_local(user_id, name, email)
            
        except Exception as e:
            print(f"Erro ao registrar usuário: {e}")
            return None
    
    def try_online_register(self, user_id, name, email):
        """Tentar registrar usuário no servidor online."""
        try:
            response = requests.post(
                f"{self.api_url}/register",
                json={
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "app_version": "1.0.0"
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def save_user_local(self, user_id, name, email):
        """Salvar usuário no banco local."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO users (id, name, email)
            VALUES (?, ?, ?)
            ''', (user_id, name, email))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None  # Email já existe
        finally:
            conn.close()
    
    def login_user(self, email):
        """Fazer login do usuário."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            user_id, name = user
            
            # Atualizar último login
            cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''', (user_id,))
            
            # Criar sessão
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=30)
            
            cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at)
            VALUES (?, ?, ?)
            ''', (session_id, user_id, expires_at))
            
            conn.commit()
            conn.close()
            
            # Sincronizar com servidor
            self.sync_user_data(user_id)
            
            return {
                "user_id": user_id,
                "name": name,
                "email": email,
                "session_id": session_id
            }
        
        conn.close()
        return None
    
    def get_current_user(self):
        """Obter usuário atual da sessão."""
        session_file = Path.home() / ".backup_manager" / "current_session.json"
        
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    session = json.load(f)
                
                # Verificar se sessão ainda é válida
                if self.validate_session(session['session_id']):
                    return session
                else:
                    session_file.unlink()  # Remover sessão expirada
            except:
                pass
        
        return None
    
    def save_current_session(self, user_data):
        """Salvar sessão atual."""
        session_file = Path.home() / ".backup_manager" / "current_session.json"
        with open(session_file, 'w') as f:
            json.dump(user_data, f)
    
    def logout_user(self):
        """Fazer logout do usuário."""
        session_file = Path.home() / ".backup_manager" / "current_session.json"
        if session_file.exists():
            session_file.unlink()
    
    def validate_session(self, session_id):
        """Validar se sessão ainda é válida."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT expires_at FROM sessions 
        WHERE id = ? AND is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            expires_at = datetime.fromisoformat(result[0])
            return datetime.now() < expires_at
        
        return False
    
    def log_user_action(self, action_type, details=None):
        """Registrar ação do usuário."""
        user = self.get_current_user()
        if not user:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO usage_stats (user_id, action_type, details)
        VALUES (?, ?, ?)
        ''', (user['user_id'], action_type, json.dumps(details) if details else None))
        
        conn.commit()
        conn.close()
        
        # Tentar sincronizar com servidor
        self.sync_usage_stats(user['user_id'], action_type, details)
    
    def update_backup_stats(self, backup_size):
        """Atualizar estatísticas de backup."""
        user = self.get_current_user()
        if not user:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE users 
        SET total_backups = total_backups + 1,
            total_size = total_size + ?
        WHERE id = ?
        ''', (backup_size, user['user_id']))
        
        conn.commit()
        conn.close()
        
        # Log da ação
        self.log_user_action('backup', {
            'size': backup_size,
            'timestamp': datetime.now().isoformat()
        })
    
    def sync_user_data(self, user_id):
        """Sincronizar dados do usuário com servidor."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter dados do usuário
            cursor.execute('''
            SELECT name, email, last_login, total_backups, total_size
            FROM users WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                requests.post(
                    f"{self.api_url}/sync_user",
                    json={
                        "user_id": user_id,
                        "name": user_data[0],
                        "email": user_data[1],
                        "last_login": user_data[2],
                        "total_backups": user_data[3],
                        "total_size": user_data[4]
                    },
                    timeout=5
                )
        except:
            pass  # Falha silenciosa se offline
    
    def sync_usage_stats(self, user_id, action_type, details):
        """Sincronizar estatísticas de uso com servidor."""
        try:
            requests.post(
                f"{self.api_url}/log_action",
                json={
                    "user_id": user_id,
                    "action_type": action_type,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=5
            )
        except:
            pass  # Falha silenciosa se offline
    
    def get_user_stats(self):
        """Obter estatísticas do usuário atual."""
        user = self.get_current_user()
        if not user:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas básicas
        cursor.execute('''
        SELECT total_backups, total_size, created_at, last_login
        FROM users WHERE id = ?
        ''', (user['user_id'],))
        
        stats = cursor.fetchone()
        
        # Estatísticas de ações recentes
        cursor.execute('''
        SELECT action_type, COUNT(*) as count
        FROM usage_stats 
        WHERE user_id = ? AND timestamp >= date('now', '-30 days')
        GROUP BY action_type
        ''', (user['user_id'],))
        
        actions = dict(cursor.fetchall())
        conn.close()
        
        if stats:
            return {
                'total_backups': stats[0],
                'total_size': stats[1],
                'member_since': stats[2],
                'last_login': stats[3],
                'actions_30days': actions
            }
        
        return None

# Instância global do gerenciador de usuários
user_manager = UserManager()