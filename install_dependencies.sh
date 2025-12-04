#!/bin/bash

# 📦 Script de Instalação Automática - Linux
# Instala todas as dependências necessárias para o compilador

set -e  # Para execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 INSTALAÇÃO AUTOMÁTICA DO COMPILADOR${NC}"
echo "=================================================="

# Detecta distribuição Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}❌ Não foi possível detectar a distribuição Linux${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 Distribuição detectada: $PRETTY_NAME${NC}"

# Verifica se é root para comandos sudo
if [[ $EUID -eq 0 ]]; then
    SUDO=""
    echo -e "${YELLOW}⚠️ Executando como root${NC}"
else
    SUDO="sudo"
    echo -e "${GREEN}✅ Executando com sudo${NC}"
fi

# Função para instalar no Ubuntu/Debian
install_ubuntu_debian() {
    echo -e "\n${BLUE}1. Atualizando repositórios...${NC}"
    $SUDO apt update

    echo -e "\n${BLUE}2. Instalando Python e ferramentas...${NC}"
    $SUDO apt install -y python3 python3-pip python3-venv python3-dev build-essential

    echo -e "\n${BLUE}3. Instalando LLVM e Clang...${NC}"
    $SUDO apt install -y llvm llvm-dev clang clang-dev

    echo -e "${GREEN}✅ Dependências do sistema instaladas${NC}"
}

# Função para instalar no Fedora/RHEL/CentOS
install_fedora_rhel() {
    echo -e "\n${BLUE}1. Atualizando sistema...${NC}"
    $SUDO dnf update -y

    echo -e "\n${BLUE}2. Instalando Python e ferramentas...${NC}"
    $SUDO dnf install -y python3 python3-pip python3-devel gcc gcc-c++ make

    echo -e "\n${BLUE}3. Instalando LLVM e Clang...${NC}"
    $SUDO dnf install -y llvm llvm-devel clang clang-devel

    echo -e "${GREEN}✅ Dependências do sistema instaladas${NC}"
}

# Função para instalar no Arch Linux
install_arch() {
    echo -e "\n${BLUE}1. Atualizando sistema...${NC}"
    $SUDO pacman -Syu --noconfirm

    echo -e "\n${BLUE}2. Instalando dependências...${NC}"
    $SUDO pacman -S --noconfirm python python-pip llvm clang base-devel

    echo -e "${GREEN}✅ Dependências do sistema instaladas${NC}"
}

# Instala dependências do sistema baseado na distribuição
case $DISTRO in
    ubuntu|debian)
        install_ubuntu_debian
        ;;
    fedora|rhel|centos|rocky|almalinux)
        install_fedora_rhel
        ;;
    arch|manjaro)
        install_arch
        ;;
    *)
        echo -e "${YELLOW}⚠️ Distribuição '$DISTRO' não suportada automaticamente${NC}"
        echo "Por favor, instale manualmente:"
        echo "- Python 3.8+"
        echo "- pip"
        echo "- LLVM/Clang"
        echo "- Build tools (gcc, make)"
        exit 1
        ;;
esac

# Verifica se Python está disponível
echo -e "\n${BLUE}4. Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✅ Python3 encontrado: $(python3 --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}✅ Python encontrado: $(python --version)${NC}"
else
    echo -e "${RED}❌ Python não encontrado após instalação${NC}"
    exit 1
fi

# Verifica se LLVM/Clang estão disponíveis
echo -e "\n${BLUE}5. Verificando LLVM/Clang...${NC}"
if command -v clang &> /dev/null; then
    echo -e "${GREEN}✅ Clang encontrado: $(clang --version | head -n1)${NC}"
else
    echo -e "${RED}❌ Clang não encontrado após instalação${NC}"
    exit 1
fi

if command -v llvm-config &> /dev/null; then
    echo -e "${GREEN}✅ LLVM encontrado: $(llvm-config --version)${NC}"
else
    echo -e "${RED}❌ LLVM não encontrado após instalação${NC}"
    exit 1
fi

# Cria ambiente virtual
echo -e "\n${BLUE}6. Criando ambiente virtual Python...${NC}"
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${YELLOW}⚠️ Ambiente virtual já existe${NC}"
fi

# Ativa ambiente virtual
echo -e "\n${BLUE}7. Ativando ambiente virtual...${NC}"
source .venv/bin/activate

# Atualiza pip
echo -e "\n${BLUE}8. Atualizando pip...${NC}"
python -m pip install --upgrade pip

# Instala dependências Python
echo -e "\n${BLUE}9. Instalando llvmlite...${NC}"
pip install llvmlite

# Verifica instalação
echo -e "\n${BLUE}10. Verificando instalação...${NC}"
if python -c "import llvmlite; print('llvmlite versão:', llvmlite.__version__)" 2>/dev/null; then
    echo -e "${GREEN}✅ llvmlite instalado corretamente${NC}"
else
    echo -e "${RED}❌ Problema na instalação do llvmlite${NC}"
    exit 1
fi

# Teste rápido
echo -e "\n${BLUE}11. Testando compilador...${NC}"
if [ -f "exemplos/exemplo_sucesso_simples.js" ]; then
    if python compile.py exemplos/exemplo_sucesso_simples.js --no-compile >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Teste básico passou${NC}"
    else
        echo -e "${YELLOW}⚠️ Teste básico falhou (mas dependências estão OK)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Arquivo de teste não encontrado${NC}"
fi

# Instruções finais
echo -e "\n${GREEN}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo "=================================================="
echo -e "${BLUE}Para usar o compilador:${NC}"
echo ""
echo "1. Ative o ambiente virtual:"
echo -e "${YELLOW}   source .venv/bin/activate${NC}"
echo ""
echo "2. Compile um programa:"
echo -e "${YELLOW}   python compile.py exemplos/exemplo_sucesso_simples.js${NC}"
echo ""
echo "3. Execute o programa:"
echo -e "${YELLOW}   ./exemplo_sucesso_simples${NC}"
echo ""
echo "4. Para testar todos os exemplos:"
echo -e "${YELLOW}   ./test_compiler.sh${NC}"
echo ""
echo -e "${BLUE}📚 Para mais informações, consulte o README.md${NC}"