# Desktop Backup Manager

Uma aplicação comple    ta de backup em português com interface gráfica e web.

## 🚀 Como Usar

### Opção 1: Versão Desktop (RECOMENDADA para drives locais)

Para acessar drives locais (C:, D:, etc.) da sua máquina:

```bash
python main.py
```

**Vantagens da versão desktop:**
- ✅ Acessa todos os drives e pastas locais (C:, D:, E:, etc.)
- ✅ Interface completa com navegação por pastas
- ✅ Detecção automática de drives Windows/Linux/Mac
- ✅ Funciona offline

### Opção 2: Versão Web (para upload de arquivos)

Para fazer backup de arquivos específicos via upload:

```bash
python web_backup.py
```

Depois acesse: http://localhost:5000

**Limitações da versão web:**
- ⚠️ Não acessa drives locais diretamente
- ✅ Permite upload de pastas e arquivos
- ✅ Interface web moderna

## 📋 Funcionalidades

### Backup
- **Compactação**: ZIP ou TAR.GZ
- **Múltiplas pastas**: Selecione várias pastas ao mesmo tempo
- **Progresso em tempo real**: Acompanhe o progresso do backup
- **Catálogo automático**: Histórico de todos os backups

### Restauração
- **Visualização**: Veja o conteúdo antes de restaurar
- **Restauração seletiva**: Escolha arquivos específicos
- **Restauração completa**: Ou restaure tudo de uma vez

### Catálogo
- **Histórico completo**: Lista de todos os backups
- **Informações detalhadas**: Data, tamanho, localização
- **Busca rápida**: Encontre backups rapidamente

## 🛠️ Estrutura do Projeto

```
├── main.py              # Aplicação desktop (tkinter)
├── web_backup.py        # Aplicação web (Flask)
├── backup_manager.py    # Lógica de backup
├── restore_manager.py   # Lógica de restauração
├── catalog_manager.py   # Gerenciamento de catálogo
├── gui_components.py    # Interface gráfica
├── utils.py            # Funções utilitárias
└── templates/          # Templates web
    └── index.html
```

## 📁 Exemplo de Uso

1. **Execute a versão desktop**: `python main.py`
2. **Na aba Backup**:
   - Clique em "Carregar Drives e Pastas"
   - Selecione as pastas que deseja fazer backup
   - Defina a pasta de destino
   - Escolha o tipo de compactação
   - Clique em "Iniciar Backup"

3. **Para restaurar**:
   - Vá na aba "Restaurar"
   - Selecione um backup do catálogo
   - Escolha os arquivos para restaurar
   - Defina onde restaurar
   - Clique em "Restaurar"

## 🔧 Requisitos

- Python 3.6+
- Bibliotecas padrão do Python (tkinter, zipfile, tarfile, etc.)
- Para versão web: Flask

```bash
pip install flask
```

## 💾 Armazenamento

- **Catálogo**: `~/.backup_manager/catalogs/`
- **Configurações**: `~/.backup_manager/settings.json`
- **Backups**: Local definido pelo usuário

## 🆘 Problemas Comuns

### "Não vejo meus drives C:, D:, etc."
- **Solução**: Use a versão desktop (`python main.py`)
- A versão web não pode acessar drives locais por segurança

### "Erro ao carregar pastas"
- **Solução**: Verifique as permissões da pasta
- Execute como administrador se necessário

### "Backup muito lento"
- **Solução**: Use ZIP ao invés de TAR.GZ para arquivos pequenos
- Evite pastas com muitos arquivos pequenos

## 📝 Licença

Este projeto é de código aberto. Use e modifique livremente.
