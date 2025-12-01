#!/bin/bash
# install_dependencies.sh - Script para instalar dependências do compilador

echo "=========================================="
echo "INSTALADOR DE DEPENDÊNCIAS DO COMPILADOR"
echo "=========================================="

# Detecta o sistema operacional
if [ -f /etc/fedora-release ]; then
    echo "Sistema detectado: Fedora"
    DISTRO="fedora"
elif [ -f /etc/debian_version ]; then
    echo "Sistema detectado: Debian/Ubuntu"
    DISTRO="debian"
else
    echo "Sistema não suportado diretamente pelo script."
    echo "Consulte o README.md para instruções manuais."
    exit 1
fi

echo ""
echo "1. Instalando dependências do sistema..."

if [ "$DISTRO" = "fedora" ]; then
    sudo dnf update -y
    sudo dnf install llvm llvm-devel clang clang-devel python3 python3-pip python3-devel -y
elif [ "$DISTRO" = "debian" ]; then
    sudo apt update
    sudo apt install llvm llvm-dev clang clang-dev python3 python3-pip python3-dev -y
fi

echo ""
echo "2. Criando ambiente virtual Python..."
python3 -m venv .venv
source .venv/bin/activate

echo ""
echo "3. Instalando dependências Python..."
pip install llvmlite

echo ""
echo "4. Verificando instalações..."
echo -n "LLVM: "
llvm-config --version 2>/dev/null || echo "ERRO"
echo -n "Clang: "
clang --version | head -1 2>/dev/null || echo "ERRO"
echo -n "Python: "
python --version 2>/dev/null || echo "ERRO"
echo -n "llvmlite: "
python -c "import llvmlite; print('OK')" 2>/dev/null || echo "ERRO"

echo ""
echo "=========================================="
echo "INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Para usar o compilador:"
echo "  source .venv/bin/activate"
echo "  python compile.py arquivo.txt"
echo ""
echo "Para ver exemplos:"
echo "  ls exemplos/"
echo ""
echo "Para mais informações, consulte o README.md"