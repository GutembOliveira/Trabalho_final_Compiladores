#!/bin/bash

# 🧪 Script de Teste do Compilador - Linux/macOS
# Testa todos os exemplos e valida o funcionamento

set -e  # Para execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 TESTE AUTOMATIZADO DO COMPILADOR${NC}"
echo "================================================="

# Verifica se Python está disponível
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python não encontrado!${NC}"
    exit 1
fi

# Define comando Python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Verifica se ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Ambiente virtual ativo: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️ Ambiente virtual não detectado${NC}"
fi

# Verifica dependências
echo -e "\n${BLUE}1. Verificando Dependências...${NC}"

if $PYTHON_CMD -c "import llvmlite" 2>/dev/null; then
    echo -e "${GREEN}✅ llvmlite disponível${NC}"
else
    echo -e "${RED}❌ llvmlite não encontrado!${NC}"
    echo "Instale com: pip install llvmlite"
    exit 1
fi

if command -v clang &> /dev/null; then
    echo -e "${GREEN}✅ clang disponível${NC}"
else
    echo -e "${RED}❌ clang não encontrado!${NC}"
    echo "Instale clang primeiro"
    exit 1
fi

# Testa exemplos com sucesso (devem compilar)
echo -e "\n${BLUE}2. Testando Exemplos com Sucesso...${NC}"

success_examples=(
    "exemplo_sucesso_simples.js"
    "exemplo_sucesso_condicional.js"  
    "exemplo_sucesso_funcoes.js"
    "exemplo_sucesso_loops.js"
    "exemplo_complexo.js"
)

success_count=0
for example in "${success_examples[@]}"; do
    echo -n "  Testando $example... "
    
    if [ -f "exemplos/$example" ]; then
        if $PYTHON_CMD compile.py "exemplos/$example" -o "test_output" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            success_count=$((success_count + 1))
            
            # Remove arquivo gerado
            rm -f test_output test_output.exe
        else
            echo -e "${RED}❌ FALHOU${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Arquivo não encontrado${NC}"
    fi
done

echo -e "  ${GREEN}Sucessos: $success_count/${#success_examples[@]}${NC}"

# Testa exemplos com erro (devem falhar na compilação)
echo -e "\n${BLUE}3. Testando Exemplos com Erro...${NC}"

error_examples=(
    "exemplo_erro_sintaxe.js"
    "exemplo_erro_semantico.js"
    "exemplo_erro_escopo.js"
)

error_count=0
for example in "${error_examples[@]}"; do
    echo -n "  Testando $example... "
    
    if [ -f "exemplos/$example" ]; then
        if $PYTHON_CMD compile.py "exemplos/$example" -o "test_error_output" >/dev/null 2>&1; then
            echo -e "${RED}❌ DEVERIA FALHAR${NC}"
        else
            echo -e "${GREEN}✅ Falhou corretamente${NC}"
            error_count=$((error_count + 1))
        fi
        
        # Remove qualquer arquivo gerado
        rm -f test_error_output test_error_output.exe
    else
        echo -e "${YELLOW}⚠️ Arquivo não encontrado${NC}"
    fi
done

echo -e "  ${GREEN}Erros detectados: $error_count/${#error_examples[@]}${NC}"

# Testa funcionalidades específicas
echo -e "\n${BLUE}4. Testando Funcionalidades Específicas...${NC}"

# Teste de tokens
echo -n "  Teste --tokens... "
if $PYTHON_CMD compile.py exemplos/exemplo_sucesso_simples.js --tokens >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALHOU${NC}"
fi

# Teste de AST
echo -n "  Teste --ast... "
if $PYTHON_CMD compile.py exemplos/exemplo_sucesso_simples.js --ast >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALHOU${NC}"
fi

# Teste de IR
echo -n "  Teste --ir... "
if $PYTHON_CMD compile.py exemplos/exemplo_sucesso_simples.js --ir >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALHOU${NC}"
fi

# Teste no-compile
echo -n "  Teste --no-compile... "
if $PYTHON_CMD compile.py exemplos/exemplo_sucesso_simples.js --no-compile >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALHOU${NC}"
fi

# Limpeza
rm -f test_output test_output.exe test_error_output test_error_output.exe
rm -f *_debug.ll

# Resumo final
total_success=$((success_count + error_count))
total_tests=$((${#success_examples[@]} + ${#error_examples[@]}))

echo -e "\n${BLUE}📊 RESUMO DOS TESTES${NC}"
echo "================================================="
echo -e "Exemplos de sucesso: ${GREEN}$success_count/${#success_examples[@]}${NC}"
echo -e "Exemplos de erro: ${GREEN}$error_count/${#error_examples[@]}${NC}"
echo -e "Total: ${GREEN}$total_success/$total_tests${NC}"

if [ $total_success -eq $total_tests ]; then
    echo -e "\n${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️ Alguns testes falharam${NC}"
    exit 1
fi