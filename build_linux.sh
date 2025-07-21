#!/bin/bash
echo "Criando executável para Linux..."
python3 build_executable.py
echo
echo "Executável criado em dist/linux_x86_64/"
read -p "Pressione Enter para continuar..."
