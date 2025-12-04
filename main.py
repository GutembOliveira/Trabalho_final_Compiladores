import sys

# Importe a classe do analisador semântico
from analisadorSintatico import SemanticAnalyzer

from codegen import LLVMCodeGenerator
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
        print("\n=== ❌ ERROS SINTÁTICOS (PARSING) ===")
        for e in parser.errors:
            print(e)
        # Se houver erros sintáticos graves, podemos parar a análise.
        return 
    else:
        print("✅ Análise Sintática OK. AST gerada.")
      
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
        print(f"\n❌ Análise Semântica FALHOU com {len(semantic_errors)} erro(s).")
    else:
        print("✅ Análise Semântica OK. Não foram encontrados erros de escopo, atribuição, ou declaração.")
    # 5. GERAÇÃO DE CÓDIGO LLVM IR
    print("\n4️⃣ Geração de Código LLVM IR...")
    # 5. GERAÇÃO DE CÓDIGO LLVM IR
    print("\n4️⃣ Geração de Código LLVM IR...")
    
    try:
        code_generator = LLVMCodeGenerator()
        llvm_ir = code_generator.generate_code(program)
        print("✅ LLVM IR gerado com sucesso")
        print("\n--- 🔧 LLVM IR GERADO ---")
        print(llvm_ir)
        # Salva IR em arquivo para debug
        ir_debug_file = Path(filename).stem + "_debug.ll"
        with open(ir_debug_file, 'w', encoding='utf-8') as f:
            f.write(llvm_ir)
        print(f"🐛 Debug: IR salvo em {ir_debug_file}")
            
    except Exception as e:
        print(f"❌ Erro na geração de código: {e}")
      
    
    

if __name__ == "__main__":
    main()