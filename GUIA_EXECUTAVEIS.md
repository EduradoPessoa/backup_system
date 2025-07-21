# Guia para Criar Executáveis
## Desktop Backup Manager - PHOENYX TECNOLOGIA © 2025

Este guia explica como criar executáveis standalone do Desktop Backup Manager para Windows, Linux e macOS.

## 🎯 Visão Geral

Os executáveis criados são **standalone** - não precisam do Python instalado no computador de destino. Isso torna a distribuição muito mais simples para usuários finais.

## 📋 Pré-requisitos

- Python 3.7 ou superior
- PyInstaller (instalado automaticamente pelos scripts)

## 🚀 Como Criar Executáveis

### Para Windows (.exe)

```batch
# Execute no Windows
build_windows.bat
```

**OU** manualmente:
```cmd
pip install pyinstaller
python build_executable.py
```

### Para Linux (binário)

```bash
# Execute no Linux
./build_linux.sh
```

**OU** manualmente:
```bash
pip3 install pyinstaller
python3 build_executable.py
```

### Para macOS (.app)

```bash
# Execute no macOS
./build_macos.sh
```

**OU** manualmente:
```bash
pip3 install pyinstaller
python3 build_executable.py
```

## 📦 Estrutura dos Executáveis

Após a criação, você encontrará:

```
dist/
├── windows_x86_64/
│   └── DesktopBackupManager/
│       ├── DesktopBackupManager.exe  ← Executável principal
│       ├── backup_cli.py             ← Interface linha de comando
│       ├── README.md                 ← Documentação
│       └── LEIA-ME.txt              ← Instruções em português
│
├── linux_x86_64/
│   └── DesktopBackupManager/
│       ├── DesktopBackupManager      ← Executável principal
│       └── [outros arquivos...]
│
└── darwin_arm64/  (ou darwin_x86_64)
    └── DesktopBackupManager/
        ├── DesktopBackupManager.app  ← Aplicativo macOS
        └── [outros arquivos...]
```

## 🎛️ Funcionalidades dos Executáveis

### Interface Gráfica
- Execute: `DesktopBackupManager` (ou `.exe` no Windows)
- Interface completa em português
- Backup de múltiplas pastas
- Compressão ZIP e TAR.GZ
- Catálogo de backups
- Restauração seletiva

### Linha de Comando
- Execute: `python backup_cli.py --help`
- Ideal para automação
- Compatível com agendadores de tarefas
- Modo verboso e relatórios detalhados

## 🔧 Personalização Avançada

### Modificar o arquivo .spec

O arquivo `backup_manager.spec` permite customizações avançadas:

```python
# Adicionar ícone personalizado
icon='path/to/icon.ico'  # Windows
icon='path/to/icon.icns'  # macOS

# Incluir arquivos adicionais
datas=[
    ('templates', 'templates'),
    ('icons', 'icons'),
    ('config', 'config'),
],

# Configurações de console
console=False,  # False = GUI, True = Console
```

### Comprimir o Executável

Para reduzir o tamanho:

```bash
# Instalar UPX (compressor)
# Windows: baixar de https://upx.github.io/
# Linux: sudo apt install upx
# macOS: brew install upx

# Usar no .spec
upx=True,
upx_exclude=[],
```

## 📤 Distribuição

### Pacote Simples
1. Compacte a pasta `dist/[sistema]/DesktopBackupManager/`
2. Envie por email ou cloud storage
3. Usuário descompacta e executa

### Instalador Profissional
Para criar instaladores:

- **Windows**: NSIS, Inno Setup, ou WiX
- **Linux**: AppImage, Snap, ou DEB/RPM
- **macOS**: criar DMG ou usar tools como create-dmg

## 🐛 Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install pyinstaller
# ou
pip3 install pyinstaller
```

### Erro: "Módulo não encontrado"
Adicione ao `hiddenimports` no arquivo .spec:
```python
hiddenimports=[
    'modulo_ausente',
    'outro_modulo',
],
```

### Executável muito grande
1. Use UPX para compressão
2. Remova módulos desnecessários
3. Use `--exclude-module` no PyInstaller

### Não executa em outro computador
1. Verifique a arquitetura (32/64 bits)
2. Teste em VM limpa
3. Inclua todas as dependências no .spec

## 📊 Tamanhos Aproximados

- **Windows**: ~50-80 MB
- **Linux**: ~45-70 MB  
- **macOS**: ~55-85 MB

## 🔒 Assinatura Digital (Opcional)

### Windows
```cmd
signtool sign /f certificado.pfx /p senha DesktopBackupManager.exe
```

### macOS
```bash
codesign --force --sign "Developer ID" DesktopBackupManager.app
```

## 📞 Suporte

Para problemas específicos:
1. Verifique o log de build
2. Teste em ambiente limpo
3. Consulte documentação do PyInstaller
4. Entre em contato com PHOENYX TECNOLOGIA

---

**PHOENYX TECNOLOGIA © 2025**  
*Soluções tecnológicas profissionais*