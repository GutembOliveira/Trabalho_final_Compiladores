import sys

# Importe a classe do analisador semântico
from analisadorSintatico import SemanticAnalyzer

from codegen import LLVMCodeGenerator, OptimizationLevel
from lexer import Lexer
from tokens import TokenType
from parser import Parser
import sys
import argparse
import os
import tempfile
from pathlib import Path

def main():
   
    filename = "source_code.txt"
    try:
        with open(filename, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        sys.exit(1)

 
    # 2) ANÁLISE LÉXICA
    # O parser consome os tokens gerados por esta instância do lexer.
    lexer_for_parser = Lexer(source_code)
    
    # 3) ANÁLISE SINTÁTICA → AST
    print("--- 1. Análise Sintática ---")
    parser = Parser(lexer_for_parser)
    program = parser.parse_program()

    # 4) Resultados da Análise Sintática
    if len(parser.errors) > 0:
        print("\n=== ERROS SINTÁTICOS (PARSING) ===")
        for e in parser.errors:
            print(e)
        # Se houver erros sintáticos graves, podemos parar a análise.
        return 
    else:
        print("Análise Sintática OK. AST gerada.")
      
    # --- INTEGRAÇÃO DA ANÁLISE SEMÂNTICA ---
    # 5) ANÁLISE SEMÂNTICA
    print("\n--- 2. Análise Semântica ---")
    
    # Cria uma instância do analisador semântico
    analyzer = SemanticAnalyzer()
    
    # Executa a análise no nó raiz da AST
    semantic_errors = analyzer.analyze(program)

    # 6) Resultados da Análise Semântica
    if semantic_errors:
        print("\n=== ⚠️ ERROS SEMÂNTICOS ===")
        for e in semantic_errors:
            print(e)
        print(f"\nAnálise Semântica FALHOU com {len(semantic_errors)} erro(s).")
    else:
        print("Análise Semântica OK. Não foram encontrados erros de escopo, atribuição, ou declaração.")
    
    # 4. GERAÇÃO DE CÓDIGO LLVM IR - VERSÃO SEM OTIMIZAÇÃO
    print("\n=== GERAÇÃO DE CÓDIGO LLVM IR ===")
    
    print("\n4️⃣ Geração de Código LLVM IR (SEM OTIMIZAÇÃO - O0)...")
    
    try:
        # Gerador sem otimização
        code_generator_no_opt = LLVMCodeGenerator(optimization_level=OptimizationLevel.O0)
        llvm_ir_no_opt = code_generator_no_opt.generate_code(program)
        print("LLVM IR (O0) gerado com sucesso")
        
        # Salva IR sem otimização em arquivo para debug
        ir_no_opt_file = Path(filename).stem + "_no_optimization.ll"
        with open(ir_no_opt_file, 'w', encoding='utf-8') as f:
            f.write(llvm_ir_no_opt)
        print(f"IR sem otimização salvo em: {ir_no_opt_file}")
        
        # Compila versão sem otimização
        output_no_opt = Path(filename).stem + "_no_opt"
        success_no_opt = code_generator_no_opt.compile_to_executable(output_no_opt)
        
        if success_no_opt:
            print(f"Executável sem otimização gerado: {output_no_opt}")
        else:
            print(f"Falha ao gerar executável sem otimização")
            
    except Exception as e:
        print(f"Erro na geração de código sem otimização: {e}")
    
    print("\n5️⃣ Geração de Código LLVM IR (COM OTIMIZAÇÃO - Os)...")
    
    try:
        # Gerador com otimização para tamanho
        code_generator_opt = LLVMCodeGenerator(optimization_level=OptimizationLevel.Os)
        llvm_ir_opt = code_generator_opt.generate_code(program)
        print("LLVM IR (Os) gerado com sucesso")
        
        # Salva IR otimizado em arquivo para debug
        ir_opt_file = Path(filename).stem + "_optimized.ll"
        with open(ir_opt_file, 'w', encoding='utf-8') as f:
            f.write(llvm_ir_opt)
        print(f"IR otimizado salvo em: {ir_opt_file}")
        
        # Compila versão otimizada
        output_opt = Path(filename).stem + "_optimized"
        success_opt = code_generator_opt.compile_to_executable(output_opt)
        
        if success_opt:
            print(f"Executável otimizado gerado: {output_opt}")
        else:
            print(f"Falha ao gerar executável otimizado")
            
        # Exibe estatísticas de otimização
        if success_opt:
            print("\nESTATÍSTICAS DE OTIMIZAÇÃO:")
            stats_opt = code_generator_opt.get_optimization_stats()
            print(f"   • Nível de otimização: {stats_opt['optimization_level']}")
            print(f"   • Tamanho do módulo IR: {stats_opt['module_size']} caracteres")
            print(f"   • Número de funções: {stats_opt.get('functions_count', 'N/A')}")
            
    except Exception as e:
        print(f"Erro na geração de código otimizado: {e}")
    
    # 6. COMPARAÇÃO DE RESULTADOS
    print("\n=== COMPARAÇÃO DE RESULTADOS ===")
    
    try:
        # Verifica se os arquivos foram gerados
        no_opt_file = Path(filename).stem + "_no_opt"
        opt_file = Path(filename).stem + "_optimized"
        
        if os.path.exists(no_opt_file) and os.path.exists(opt_file):
            no_opt_size = os.path.getsize(no_opt_file)
            opt_size = os.path.getsize(opt_file)
            
            print(f"Tamanho executável sem otimização (O0): {no_opt_size} bytes")
            print(f"Tamanho executável otimizado (Os): {opt_size} bytes")
            
            if opt_size < no_opt_size:
                reduction = ((no_opt_size - opt_size) / no_opt_size) * 100
                print(f"Redução de tamanho: {reduction:.1f}%")
            elif opt_size > no_opt_size:
                increase = ((opt_size - no_opt_size) / no_opt_size) * 100
                print(f"Aumento de tamanho: {increase:.1f}% (normal com otimizações agressivas)")
            else:
                print("Tamanhos iguais")
                
            print(f"\nPara executar sem otimização: ./{no_opt_file}")
            print(f"Para executar com otimização: ./{opt_file}")
        else:
            print("Não foi possível comparar - alguns executáveis não foram gerados")
            
    except Exception as e:
        print(f"Erro na comparação: {e}")
      
    
    

if __name__ == "__main__":
    main()