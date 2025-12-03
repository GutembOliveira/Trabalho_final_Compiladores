import sys

# Importe a classe do analisador semântico
from analisadorSintatico import SemanticAnalyzer

from lexer import Lexer
from tokens import TokenType
from parser import Parser

def main():
    # Esta função tokenize não é mais usada, mas a mantenho comentada se for um requisito.
    # def tokenize(source):
    #     lexer = Lexer(source)
    #     tokens = []
    #     tok = lexer.next_token()
    #     while tok.type != TokenType.EOF:
    #         tokens.append(tok)
    #         tok = lexer.next_token()
    #     tokens.append(tok)  # adiciona o EOF
    #     return tokens

    # 1) LEITURA DO CÓDIGO FONTE
    # O seu código original já trata da leitura
    # filename = sys.argv[1] # Se for usar linha de comando
    filename = "source_code.txt"
    try:
        with open(filename, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        sys.exit(1)

    # Inicializamos o lexer duas vezes ou resetamos ele
    # Nota: Em Python, a passagem de objetos pode ser complexa. 
    # É mais seguro criar uma nova instância para o Parser usar.
    
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
        # Opcionalmente, imprime a AST:
        # print("\n--- AST ---")
        # print(program)
    
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

if __name__ == "__main__":
    main()