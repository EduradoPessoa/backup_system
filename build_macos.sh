#!/bin/bash

echo "================================================================"
echo "   DESKTOP BACKUP MANAGER - CRIADOR DE EXECUTÁVEL MACOS"
echo "                PHOENYX TECNOLOGIA 2025"
echo "================================================================"
echo

echo "Verificando dependências..."
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERRO: PyInstaller não encontrado!"
    echo "Instalando PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao instalar PyInstaller"
        echo "Tente instalar com Homebrew:"
        echo "brew install python"
        echo "pip3 install pyinstaller"
        exit 1
    fi
fi

echo
echo "Criando executável para macOS..."
python3 build_executable.py

echo
echo "Criando pacote .app para macOS..."
# Criar estrutura .app se necessário
APP_NAME="DesktopBackupManager.app"
if [ -d "dist/darwin_*/DesktopBackupManager" ]; then
    DIST_DIR=$(find dist -name "darwin_*" -type d)
    EXE_DIR="$DIST_DIR/DesktopBackupManager"
    
    mkdir -p "$DIST_DIR/$APP_NAME/Contents/MacOS"
    mkdir -p "$DIST_DIR/$APP_NAME/Contents/Resources"
    
    # Copiar executável
    cp -r "$EXE_DIR"/* "$DIST_DIR/$APP_NAME/Contents/MacOS/"
    
    # Criar Info.plist
    cat > "$DIST_DIR/$APP_NAME/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DesktopBackupManager</string>
    <key>CFBundleIdentifier</key>
    <string>com.phoenyx.desktopbackupmanager</string>
    <key>CFBundleName</key>
    <string>Desktop Backup Manager</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    echo "✓ Pacote .app criado: $DIST_DIR/$APP_NAME"
fi

echo
echo "================================================================"
echo "                        CONCLUÍDO!"
echo "================================================================"
echo
echo "O executável foi criado na pasta dist/"
echo "Você pode distribuir essa pasta para outros computadores macOS."
echo
read -p "Pressione Enter para continuar..."