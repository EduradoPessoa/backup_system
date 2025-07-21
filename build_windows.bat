@echo off
echo ================================================================
echo    DESKTOP BACKUP MANAGER - CRIADOR DE EXECUTAVEL WINDOWS
echo                PHOENYX TECNOLOGIA 2025
echo ================================================================
echo.

echo Verificando dependencias...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERRO: PyInstaller nao encontrado!
    echo Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERRO: Falha ao instalar PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Criando executavel para Windows...
python build_executable.py

echo.
echo ================================================================
echo                        CONCLUIDO!
echo ================================================================
echo.
echo O executavel foi criado na pasta dist\
echo Voce pode distribuir essa pasta para outros computadores Windows.
echo.
pause