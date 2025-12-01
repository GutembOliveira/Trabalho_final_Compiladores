#!/usr/bin/env python3
# compile.py - Script principal de compilação

import sys
import os
import argparse
from lexer import Lexer
from parser import Parser
from codegen import LLVMCodeGenerator

def main():
    parser = argparse.ArgumentParser(description='Compilador para a linguagem personalizada')
    parser.add_argument('input_file', help='Arquivo de código fonte')
    parser.add_argument('-o', '--output', default='program', help='Nome do executável de saída')
    parser.add_argument('--ir', action='store_true', help='Mostra o código LLVM IR gerado')
    parser.add_argument('--tokens', action='store_true', help='Mostra os tokens gerados')
    parser.add_argument('--ast', action='store_true', help='Mostra a árvore sintática')
    parser.add_argument('--no-compile', action='store_true', help='Não compila o executável')
    
    args = parser.parse_args()
    
    # Verifica se o arquivo existe
    if not os.path.exists(args.input_file):
        print(f"Erro: Arquivo '{args.input_file}' não encontrado")
        return 1
        
    # Lê o código fonte
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return 1
        
    print(f"Compilando arquivo: {args.input_file}")
    print("=" * 50)
    
    # 1. Análise Léxica
    print("1. Análise Léxica...")
    lexer = Lexer(source_code)
    
    if args.tokens:
        print("\n--- TOKENS ---")
        lexer_copy = Lexer(source_code)
        while True:
            token = lexer_copy.next_token()
            print(token)
            if token.type.name == 'EOF':
                break
        print()
    
    # 2. Análise Sintática
    print("2. Análise Sintática...")
    parser_obj = Parser(lexer)
    program = parser_obj.parse_program()
    
    # Verifica erros de parsing
    if len(parser_obj.errors) > 0:
        print("\n❌ ERROS DE PARSING:")
        for error in parser_obj.errors:
            print(f"  {error}")
        return 1
        
    print("✅ Análise sintática concluída com sucesso")
    
    if args.ast:
        print("\n--- AST ---")
        print(program)
        print()
    
    # 3. Geração de Código
    print("3. Geração de código LLVM IR...")
    try:
        codegen = LLVMCodeGenerator()
        llvm_ir = codegen.generate_code(program)
        print("✅ Código LLVM IR gerado com sucesso")
        
        if args.ir:
            print("\n--- LLVM IR ---")
            print(llvm_ir)
            print()
            
    except Exception as e:
        print(f"❌ Erro na geração de código: {e}")
        return 1
        
    # 4. Compilação para executável
    if not args.no_compile:
        print("4. Compilando para executável...")
        try:
            codegen.compile_to_executable(args.output)
            print(f"✅ Compilação concluída: {args.output}")
            
            # Instruções para execução
            print("\n" + "=" * 50)
            print(f"Para executar o programa:")
            print(f"  ./{args.output}")
            
        except Exception as e:
            print(f"❌ Erro na compilação final: {e}")
            return 1
    else:
        print("4. Compilação pulada (--no-compile)")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
