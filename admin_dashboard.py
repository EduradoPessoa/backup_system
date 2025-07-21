#!/usr/bin/env python3
"""
Painel Administrativo Web
Desktop Backup Manager - PHOENYX TECNOLOGIA © 2025
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib

app = Flask(__name__)
app.secret_key = "phoenyx_admin_2025_secret_key"

# Configurações do administrador
ADMIN_PASSWORD_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password"

def get_admin_db_path():
    """Obter caminho do banco de dados administrativo."""
    return Path.home() / ".backup_manager_admin" / "admin.db"

def init_admin_database():
    """Inicializar banco de dados administrativo."""
    db_path = get_admin_db_path()
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabela de usuários consolidada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consolidated_users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP,
        last_login TIMESTAMP,
        total_backups INTEGER DEFAULT 0,
        total_size INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de estatísticas globais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS global_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT,
        metric_value TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de logs de ações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS action_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        action_type TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

def collect_user_data():
    """Coletar dados de usuários de todos os bancos locais."""
    users_data = []
    
    # Procurar por bancos de usuários
    backup_dirs = [
        Path.home() / ".backup_manager",
        Path("/tmp/backup_manager_users"),  # Para ambiente de desenvolvimento
    ]
    
    for backup_dir in backup_dirs:
        if backup_dir.exists():
            db_file = backup_dir / "users.db"
            if db_file.exists():
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    SELECT id, name, email, created_at, last_login, 
                           total_backups, total_size, is_active
                    FROM users
                    ''')
                    
                    for row in cursor.fetchall():
                        users_data.append({
                            'id': row[0],
                            'name': row[1],
                            'email': row[2],
                            'created_at': row[3],
                            'last_login': row[4],
                            'total_backups': row[5],
                            'total_size': row[6],
                            'is_active': row[7]
                        })
                    
                    conn.close()
                except Exception as e:
                    print(f"Erro ao ler {db_file}: {e}")
    
    return users_data

def update_consolidated_data():
    """Atualizar dados consolidados."""
    users_data = collect_user_data()
    
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Limpar dados antigos
    cursor.execute('DELETE FROM consolidated_users')
    
    # Inserir dados atualizados
    for user in users_data:
        cursor.execute('''
        INSERT OR REPLACE INTO consolidated_users 
        (id, name, email, created_at, last_login, total_backups, total_size, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['id'], user['name'], user['email'], user['created_at'],
            user['last_login'], user['total_backups'], user['total_size'], user['is_active']
        ))
    
    # Atualizar estatísticas globais
    total_users = len(users_data)
    active_users = len([u for u in users_data if u['is_active']])
    total_backups = sum(u['total_backups'] for u in users_data)
    total_size = sum(u['total_size'] for u in users_data)
    
    stats = [
        ('total_users', str(total_users)),
        ('active_users', str(active_users)),
        ('total_backups', str(total_backups)),
        ('total_size', str(total_size)),
    ]
    
    cursor.execute('DELETE FROM global_stats WHERE timestamp < datetime("now", "-1 hour")')
    
    for metric_name, metric_value in stats:
        cursor.execute('''
        INSERT INTO global_stats (metric_name, metric_value)
        VALUES (?, ?)
        ''', (metric_name, metric_value))
    
    conn.commit()
    conn.close()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Página de login administrativo."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == ADMIN_PASSWORD_HASH:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('admin_login.html', error="Senha incorreta")
        else:
            return render_template('admin_login.html', error="Digite a senha")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout administrativo."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    """Dashboard administrativo principal."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Atualizar dados
    update_consolidated_data()
    
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obter estatísticas globais
    cursor.execute('''
    SELECT metric_name, metric_value 
    FROM global_stats 
    WHERE timestamp = (SELECT MAX(timestamp) FROM global_stats)
    ''')
    
    stats = dict(cursor.fetchall())
    
    # Obter usuários recentes
    cursor.execute('''
    SELECT name, email, created_at, last_login, total_backups, total_size
    FROM consolidated_users 
    ORDER BY created_at DESC 
    LIMIT 10
    ''')
    
    recent_users = cursor.fetchall()
    
    # Obter usuários mais ativos
    cursor.execute('''
    SELECT name, email, total_backups, total_size
    FROM consolidated_users 
    ORDER BY total_backups DESC 
    LIMIT 10
    ''')
    
    active_users = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         active_users=active_users)

@app.route('/admin/users')
def admin_users():
    """Lista completa de usuários."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    update_consolidated_data()
    
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, email, created_at, last_login, total_backups, total_size, is_active
    FROM consolidated_users 
    ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/api/stats')
def admin_api_stats():
    """API para estatísticas em tempo real."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    update_consolidated_data()
    
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Estatísticas por período
    cursor.execute('''
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as new_users
    FROM consolidated_users 
    WHERE created_at >= date('now', '-30 days')
    GROUP BY DATE(created_at)
    ORDER BY date
    ''')
    
    daily_registrations = cursor.fetchall()
    
    # Distribuição de tamanhos de backup
    cursor.execute('''
    SELECT 
        CASE 
            WHEN total_size < 1024*1024*1024 THEN 'Menos de 1GB'
            WHEN total_size < 5*1024*1024*1024 THEN '1-5GB'
            WHEN total_size < 10*1024*1024*1024 THEN '5-10GB'
            ELSE 'Mais de 10GB'
        END as size_range,
        COUNT(*) as count
    FROM consolidated_users
    WHERE total_size > 0
    GROUP BY size_range
    ''')
    
    size_distribution = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'daily_registrations': daily_registrations,
        'size_distribution': size_distribution
    })

# Rotas da API para receber dados dos clientes
@app.route('/api/register', methods=['POST'])
def api_register():
    """API para registro de usuários."""
    data = request.get_json()
    
    # Log do registro
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO action_logs (user_id, action_type, details)
    VALUES (?, ?, ?)
    ''', (data.get('user_id'), 'register', json.dumps(data)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/sync_user', methods=['POST'])
def api_sync_user():
    """API para sincronização de dados do usuário."""
    data = request.get_json()
    
    # Atualizar dados do usuário
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO consolidated_users 
    (id, name, email, last_login, total_backups, total_size, last_sync)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (
        data.get('user_id'), data.get('name'), data.get('email'),
        data.get('last_login'), data.get('total_backups'), data.get('total_size')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/log_action', methods=['POST'])
def api_log_action():
    """API para log de ações dos usuários."""
    data = request.get_json()
    
    db_path = get_admin_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO action_logs (user_id, action_type, details, timestamp)
    VALUES (?, ?, ?, ?)
    ''', (
        data.get('user_id'), data.get('action_type'), 
        json.dumps(data.get('details')), data.get('timestamp')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_admin_database()
    app.run(host='0.0.0.0', port=5001, debug=True)