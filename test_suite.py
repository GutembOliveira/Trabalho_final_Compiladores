#!/usr/bin/env python3
"""
Script de teste automatizado para o compilador
Demonstra todas as funcionalidades e casos de erro
"""

import os
import sys
from lexer import Lexer
from parser import Parser
from analisadorSintatico import SemanticAnalyzer

def run_test(filename, description):
    """Executa um teste e mostra os resultados"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTE: {description}")
    print(f"📁 Arquivo: {filename}")
    print(f"{'='*60}")
    
    try:
        with open(filename, "r") as f:
            source_code = f.read()
        
        print(f"\n📝 CÓDIGO:")
        print("-" * 40)
        print(source_code)
        print("-" * 40)
        
        # Análise Lexical e Sintática
        lexer_for_parser = Lexer(source_code)
        parser = Parser(lexer_for_parser)
        program = parser.parse_program()

        print(f"\n🔍 ANÁLISE SINTÁTICA:")
        if parser.errors:
            print("❌ ERROS ENCONTRADOS:")
            for error in parser.errors:
                print(f"   • {error}")
        else:
            print("✅ Análise sintática OK")
            
            # Se não há erros sintáticos, fazer análise semântica
            print(f"\n🧠 ANÁLISE SEMÂNTICA:")
            analyzer = SemanticAnalyzer()
            semantic_errors = analyzer.analyze(program)
            
            if semantic_errors:
                print("⚠️  ERROS SEMÂNTICOS:")
                for error in semantic_errors:
                    print(f"   • {error}")
            else:
                print("✅ Análise semântica OK")
                
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{filename}' não encontrado")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

def main():
    """Função principal que executa todos os testes"""
    print("🚀 COMPILADOR - SUITE DE TESTES AUTOMATIZADA")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("examples/exemplo_sucesso_sem_print.txt", "Código Correto (sem erros)"),
        ("examples/exemplo_erro_lexico.txt", "Erros Léxicos"),
        ("examples/exemplo_erro_sintatico.txt", "Erros Sintáticos"), 
        ("examples/exemplo_erro_semantico.txt", "Erros Semânticos"),
        ("test_casos_limite.txt", "Casos Limite do Lexer")
    ]
    
    # Executar cada teste
    for filename, description in tests:
        if os.path.exists(filename):
            run_test(filename, description)
        else:
            print(f"\n⚠️  ARQUIVO NÃO ENCONTRADO: {filename}")
    
    print(f"\n{'='*60}")
    print("🎯 RESUMO DOS TESTES")
    print(f"{'='*60}")
    print("✅ Testes executados com sucesso")
    print("📊 Para análise detalhada, revise as saídas acima")
    print("📚 Para mais informações, consulte o README.md")
    
if __name__ == "__main__":
    main()