#!/usr/bin/env python3
"""
🚀 Compilador Completo - Frontend + Backend
==========================================

Script principal que executa todo o pipeline de compilação:
1. Análise Léxica (Lexer)
2. Análise Sintática (Parser) 
3. Análise Semântica (Semantic Analyzer)
4. Geração de Código LLVM IR (Code Generator)
5. Compilação para Executável

Uso:
    python compile.py <arquivo_fonte> [opções]
    
Exemplos:
    python compile.py programa.txt
    python compile.py programa.txt -o meu_programa
    python compile.py programa.txt --tokens
    python compile.py programa.txt --ast
    python compile.py programa.txt --ir
    python compile.py programa.txt --debug
"""

import sys
import argparse
import os
import tempfile
from pathlib import Path

# Imports do frontend
from lexer import Lexer
from tokens import TokenType, Token
from parser import Parser

# Import do backend
from codegen import LLVMCodeGenerator

# Import do analisador semântico (se disponível)
try:
    from analisadorSintatico import SemanticAnalyzer
    SEMANTIC_ANALYZER_AVAILABLE = True
except ImportError:
    SEMANTIC_ANALYZER_AVAILABLE = False
    print("⚠️ Analisador semântico não disponível (analisadorSintatico.py)")

def print_banner():
    """Imprime banner do compilador"""
    banner = f"""
{'='*60}
🚀 COMPILADOR COMPLETO - Frontend + Backend
{'='*60}
"""
    print(banner)

def print_tokens(source_code):
    """Imprime todos os tokens do código fonte"""
    print("\n--- 📋 TOKENS GERADOS ---")
    lexer = Lexer(source_code)
    tokens = []
    
    while True:
        token = lexer.next_token()
        tokens.append(token)
        print(f"  {token}")
        if token.type == TokenType.EOF:
            break
    
    print(f"\n✅ Total de tokens: {len(tokens)}")
    return tokens

def print_ast(ast_node, indent=0):
    """Imprime a AST de forma hierárquica"""
    spacing = "  " * indent
    node_type = type(ast_node).__name__
    
    if hasattr(ast_node, '__dict__'):
        print(f"{spacing}{node_type}:")
        for attr, value in ast_node.__dict__.items():
            print(f"{spacing}  {attr}:", end=" ")
            if hasattr(value, '__dict__') and hasattr(value, '__class__'):
                print()
                print_ast(value, indent + 2)
            elif isinstance(value, list):
                print(f"[{len(value)} items]")
                for i, item in enumerate(value):
                    if hasattr(item, '__dict__') and hasattr(item, '__class__'):
                        print(f"{spacing}    [{i}]:")
                        print_ast(item, indent + 3)
                    else:
                        print(f"{spacing}    [{i}]: {item}")
            else:
                print(value)
    else:
        print(f"{spacing}{node_type}: {ast_node}")

def compile_file(filename, output_name=None, show_tokens=False, show_ast=False, 
                show_ir=False, no_compile=False, debug=False):
    """Função principal de compilação"""
    
    # 1. LEITURA DO CÓDIGO FONTE
    print(f"📂 Lendo arquivo: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        print(f"✅ Arquivo lido ({len(source_code)} caracteres)")
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{filename}' não encontrado.")
        return False
    except UnicodeDecodeError:
        print(f"❌ Erro: Problema de encoding no arquivo '{filename}'.")
        return False

    print("=" * 50)
    
    # 2. ANÁLISE LÉXICA
    print("1️⃣ Análise Léxica...")
    if show_tokens:
        print_tokens(source_code)
    else:
        # Apenas verifica se há tokens válidos
        lexer = Lexer(source_code)
        token_count = 0
        while True:
            token = lexer.next_token()
            token_count += 1
            if token.type == TokenType.EOF:
                break
        print(f"✅ Análise Léxica OK ({token_count} tokens)")
    
    # 3. ANÁLISE SINTÁTICA → AST
    print("\n2️⃣ Análise Sintática...")
    lexer_for_parser = Lexer(source_code)
    parser = Parser(lexer_for_parser)
    
    try:
        ast = parser.parse_program()
    except Exception as e:
        print(f"❌ Erro durante parsing: {e}")
        return False
    
    # Verifica erros de parsing
    if len(parser.errors) > 0:
        print(f"\n❌ ERROS SINTÁTICOS ({len(parser.errors)}):")
        for i, error in enumerate(parser.errors, 1):
            print(f"  {i}. {error}")
        return False
    else:
        print("✅ Análise Sintática OK")
        
    if show_ast:
        print("\n--- 🌳 AST GERADA ---")
        print_ast(ast)
    
    # 4. ANÁLISE SEMÂNTICA (se disponível)
    if SEMANTIC_ANALYZER_AVAILABLE:
        print("\n3️⃣ Análise Semântica...")
        analyzer = SemanticAnalyzer()
        semantic_errors = analyzer.analyze(ast)
        
        if semantic_errors:
            print(f"\n❌ ERROS SEMÂNTICOS ({len(semantic_errors)}):")
            for i, error in enumerate(semantic_errors, 1):
                print(f"  {i}. {error}")
            return False
        else:
            print("✅ Análise Semântica OK")
    else:
        print("\n⚠️ Análise Semântica pulada (não disponível)")
    
    # 5. GERAÇÃO DE CÓDIGO LLVM IR
    print("\n4️⃣ Geração de Código LLVM IR...")
    
    try:
        code_generator = LLVMCodeGenerator()
        llvm_ir = code_generator.generate_code(ast)
        print("✅ LLVM IR gerado com sucesso")
        
        if show_ir:
            print("\n--- 🔧 LLVM IR GERADO ---")
            print(llvm_ir)
        
        if debug:
            # Salva IR em arquivo para debug
            ir_debug_file = Path(filename).stem + "_debug.ll"
            with open(ir_debug_file, 'w', encoding='utf-8') as f:
                f.write(llvm_ir)
            print(f"🐛 Debug: IR salvo em {ir_debug_file}")
            
    except Exception as e:
        print(f"❌ Erro na geração de código: {e}")
        if debug:
            import traceback
            print("Stack trace:")
            traceback.print_exc()
        return False
    
    # 6. COMPILAÇÃO PARA EXECUTÁVEL
    if not no_compile:
        print("\n5️⃣ Compilação para Executável...")
        
        if output_name is None:
            output_name = Path(filename).stem
            if sys.platform.startswith('win'):
                output_name += '.exe'
        
        try:
            success = code_generator.compile_to_executable(output_name)
            if success:
                print(f"🎉 Compilação CONCLUÍDA!")
                print(f"📁 Executável: {output_name}")
                
                # Instruções de execução
                if sys.platform.startswith('win'):
                    print(f"▶️ Para executar: {output_name}")
                else:
                    print(f"▶️ Para executar: ./{output_name}")
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Erro na compilação final: {e}")
            if debug:
                import traceback
                print("Stack trace:")
                traceback.print_exc()
            return False
    else:
        print("\n⏹️ Compilação pulada (--no-compile)")
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="🚀 Compilador Completo - Frontend + Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python compile.py programa.txt                 # Compilar programa
  python compile.py programa.txt -o meu_app     # Especificar nome do executável
  python compile.py programa.txt --tokens       # Mostrar tokens
  python compile.py programa.txt --ast          # Mostrar AST
  python compile.py programa.txt --ir           # Mostrar LLVM IR
  python compile.py programa.txt --debug        # Modo debug (verbose)
  python compile.py programa.txt --no-compile   # Só gerar IR, não compilar
        """
    )
    
    parser.add_argument('filename', help='Arquivo fonte para compilar')
    parser.add_argument('-o', '--output', help='Nome do executável de saída')
    parser.add_argument('--tokens', action='store_true', help='Mostrar tokens gerados')
    parser.add_argument('--ast', action='store_true', help='Mostrar AST gerada')
    parser.add_argument('--ir', action='store_true', help='Mostrar LLVM IR gerado')
    parser.add_argument('--debug', action='store_true', help='Modo debug (verbose)')
    parser.add_argument('--no-compile', action='store_true', help='Não compilar para executável')
    
    args = parser.parse_args()
    
    # Validações
    if not os.path.exists(args.filename):
        print(f"❌ Erro: Arquivo '{args.filename}' não existe.")
        sys.exit(1)
    
    # Banner
    if not any([args.tokens, args.ast, args.ir]):  # Só mostra se não for modo verbose
        print_banner()
    
    # Compilação
    success = compile_file(
        filename=args.filename,
        output_name=args.output,
        show_tokens=args.tokens,
        show_ast=args.ast,
        show_ir=args.ir,
        no_compile=args.no_compile,
        debug=args.debug
    )
    
    if success:
        print(f"\n🎯 Sucesso! Arquivo '{args.filename}' compilado com sucesso.")
        sys.exit(0)
    else:
        print(f"\n💥 Falha! Não foi possível compilar '{args.filename}'.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)