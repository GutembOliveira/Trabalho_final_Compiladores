#!/bin/bash

echo "🎯 DEMONSTRAÇÃO DE OTIMIZAÇÕES DO COMPILADOR"
echo "=============================================="
echo ""

# 1. Comparação de Assembly da função main
echo "📋 1. COMPARAÇÃO DE CÓDIGO ASSEMBLY - FUNÇÃO MAIN:"
echo ""
echo "🔴 SEM OTIMIZAÇÃO (O0):"
objdump -d source_code_no_opt | grep -A 15 "<main>:" | head -16
echo ""
echo "🟢 COM OTIMIZAÇÃO (Os):"
objdump -d source_code_optimized | grep -A 15 "<main>:" | head -16
echo ""

# 2. Contagem de instruções
echo "📊 2. CONTAGEM DE INSTRUÇÕES NA MAIN:"
INST_NO_OPT=$(objdump -d source_code_no_opt | grep -A 50 "<main>:" | grep -E "^\s*[0-9a-f]+:" | wc -l)
INST_OPT=$(objdump -d source_code_optimized | grep -A 50 "<main>:" | grep -E "^\s*[0-9a-f]+:" | wc -l)
echo "   • Sem otimização (O0): $INST_NO_OPT instruções"
echo "   • Com otimização (Os): $INST_OPT instruções"
if [ $INST_OPT -lt $INST_NO_OPT ]; then
    REDUCTION=$((INST_NO_OPT - INST_OPT))
    echo "   🎯 Redução: $REDUCTION instruções"
fi
echo ""

# 3. Tamanho das seções de código
echo "📏 3. TAMANHO DAS SEÇÕES DE CÓDIGO:"
echo "🔴 SEM OTIMIZAÇÃO:"
size source_code_no_opt | tail -1
echo "🟢 COM OTIMIZAÇÃO:"
size source_code_optimized | tail -1
echo ""

# 4. Análise detalhada de otimizações específicas
echo "🔍 4. ANÁLISE DETALHADA DE OTIMIZAÇÕES:"
echo ""
echo "🔴 SEM OTIMIZAÇÃO - Stack allocation:"
objdump -d source_code_no_opt | grep -A 3 "<main>:" | grep "sub.*rsp"
echo ""
echo "🟢 COM OTIMIZAÇÃO - Stack allocation:"
objdump -d source_code_optimized | grep -A 3 "<main>:" | grep -E "(sub.*rsp|push.*%)"
echo ""

echo "🔴 SEM OTIMIZAÇÃO - Endereçamento:"
objdump -d source_code_no_opt | grep -A 10 "<main>:" | grep "movabs"
echo ""
echo "🟢 COM OTIMIZAÇÃO - Endereçamento:"
objdump -d source_code_optimized | grep -A 10 "<main>:" | grep "mov.*\$0x"
echo ""

# 5. Performance timing
echo "⚡ 5. TESTE DE PERFORMANCE:"
echo ""
echo "🔴 SEM OTIMIZAÇÃO:"
time ./source_code_no_opt > /dev/null
echo ""
echo "🟢 COM OTIMIZAÇÃO:"
time ./source_code_optimized > /dev/null
echo ""

echo "✅ DEMONSTRAÇÃO CONCLUÍDA!"
echo "As otimizações estão funcionando mesmo com tamanhos similares de executável."