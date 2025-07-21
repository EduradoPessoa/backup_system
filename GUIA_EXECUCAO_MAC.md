# 🍎 GUIA DE EXECUÇÃO NO MAC

## 📋 Pré-requisitos

### 1. Python 3.8 ou superior
```bash
# Verificar se Python está instalado
python3 --version

# Se não estiver, instalar via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

### 2. Dependências do sistema
```bash
# Instalar tkinter (geralmente já incluído no Python do Mac)
# Se necessário:
brew install python-tk
```

## 🚀 Métodos de Execução

### Método 1: Execução Direta (Recomendado)

```bash
# 1. Baixar ou clonar o projeto
cd ~/Downloads/phoenyx-backup-manager

# 2. Instalar dependências Python
pip3 install py7zr flask

# 3. Executar aplicativo desktop
python3 main.py

# OU executar interface web
python3 web_backup.py
```

### Método 2: Ambiente Virtual (Mais Seguro)

```bash
# 1. Criar ambiente virtual
python3 -m venv venv_backup

# 2. Ativar ambiente
source venv_backup/bin/activate

# 3. Instalar dependências
pip install py7zr flask

# 4. Executar aplicativo
python main.py
```

### Método 3: Criar Aplicativo .app (Nativo Mac)

```bash
# 1. Instalar PyInstaller
pip3 install pyinstaller

# 2. Criar aplicativo nativo
python3 build_macos.sh

# 3. O aplicativo será criado em dist/
# Mover para Applications:
mv dist/PHOENYXBackupManager.app /Applications/
```

## 🔧 Script de Construção para Mac

O arquivo `build_macos.sh` automatiza a criação do executável:

```bash
#!/bin/bash
echo "🍎 Construindo PHOENYX Backup Manager para macOS..."

# Instalar dependências
pip3 install pyinstaller py7zr

# Criar aplicativo
pyinstaller --onefile --windowed \
    --name "PHOENYXBackupManager" \
    --icon=assets/icon.icns \
    --add-data "templates:templates" \
    --hidden-import tkinter \
    --hidden-import py7zr \
    main.py

echo "✅ Aplicativo criado em: dist/PHOENYXBackupManager.app"
echo "📁 Para instalar: mv dist/PHOENYXBackupManager.app /Applications/"
```

## 🛠️ Resolução de Problemas Comuns

### Problema: "tkinter não encontrado"
```bash
# Solução 1: Reinstalar Python com tkinter
brew uninstall python
brew install python-tk

# Solução 2: Usar Python do sistema
/usr/bin/python3 main.py
```

### Problema: "Permissão negada"
```bash
# Dar permissão de execução
chmod +x main.py
chmod +x build_macos.sh

# Executar com sudo se necessário
sudo python3 main.py
```

### Problema: "py7zr não instalado"
```bash
# Instalar dependência específica para 7Z
pip3 install py7zr --user
```

### Problema: "Aplicativo não abre no macOS Catalina+"
1. **Ir para Preferências do Sistema > Segurança e Privacidade**
2. **Permitir execução do aplicativo não identificado**
3. **Ou assinar digitalmente o aplicativo (para distribuição)**

## 📱 Interfaces Disponíveis

### 1. Aplicativo Desktop (Nativo)
```bash
python3 main.py
```
- Interface gráfica completa em português
- Sistema de login integrado
- Backup incremental e múltiplos formatos

### 2. Interface Web (Browser)
```bash
python3 web_backup.py
# Abrir: http://localhost:5000
```
- Interface moderna no navegador
- Não requer instalação de GUI
- Funciona em qualquer Mac com browser

### 3. Linha de Comando (Automação)
```bash
python3 backup_cli.py --help
```
- Ideal para scripts e automação
- Compatível com cron jobs do macOS
- Perfeito para backups agendados

## 🔄 Configuração de Backup Automático no macOS

### Usando crontab:
```bash
# Editar crontab
crontab -e

# Adicionar linha para backup diário às 2h da manhã
0 2 * * * /usr/bin/python3 /caminho/para/backup_cli.py backup /Users/username/Documents /Volumes/BackupDisk --title "Backup Diário" --incremental
```

### Usando Automator (GUI):
1. **Abrir Automator**
2. **Criar novo "Calendar Alarm"**
3. **Adicionar ação "Run Shell Script"**
4. **Inserir comando do backup**
5. **Salvar e agendar no Calendário**

## 📁 Estrutura de Pastas Recomendada no Mac

```
/Users/username/
├── Documents/
│   └── Backups/          # Destino dos backups
├── Applications/
│   └── PHOENYXBackupManager.app  # Aplicativo instalado
└── .backup_manager/      # Configurações e catálogo
    ├── catalogs/
    └── reports/
```

## 🔐 Permissões Necessárias

O aplicativo pode solicitar permissões para:
- **Acesso a arquivos e pastas**
- **Acesso a discos externos**
- **Execução em segundo plano** (para backups longos)

**Conceder estas permissões em Preferências do Sistema > Segurança e Privacidade**

---

**✅ Pronto!** Agora você pode usar o PHOENYX Backup Manager no seu Mac com interface nativa e todos os recursos disponíveis.

**📞 Suporte**: Se tiver problemas, use o formulário de reporte ou contate suporte@phoenyx.com.br