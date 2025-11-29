import sys

from antlr4 import FileStream
from lexer import Lexer
from tokens import TokenType
from antlr4 import FileStream, CommonTokenStream
from parser import Parser

def main():
   

    def tokenize(source):
        lexer = Lexer(source)
        tokens = []

        tok = lexer.next_token()
        while tok.type != TokenType.EOF:
            tokens.append(tok)
            tok = lexer.next_token()
        tokens.append(tok)  # adiciona o EOF

        return tokens


    # source_code = """
    # function soma(a: number, b: number) -> number {
    #     var resultado = a + b;
    #     return resultado;
    # }

    # const x = 10;
    # let y = "hello"; // 'let' será tratado como IDENT, pois não é palavra-chave

    # if (x > 5) {
    #     println("Maior que 5");
    # }"""

    #Código de exemplo para testar o lexer
    #filename = sys.argv[1]
    filename = "source_code.txt"
    with open(filename, "r") as f:
       source_code = f.read()

    lexer = Lexer(source_code)
    lexer_aux = lexer

   
    
    # print("--- Análise Léxica ---")
    # while True:
    #     token = lexer.next_token()
    #     if token.type == TokenType.EOF:
    #         print(token)
    #         break
    #     print(token)
     # 2) PARSER → AST
    parser = Parser(lexer_aux)
    program = parser.parse_program()

    # 3) Resultados
    if len(parser.errors) > 0:
        print("\n=== ERROS DE PARSING ===")
        for e in parser.errors:
            print(e)
    else:
        print("\n--- Análise Sintática OK ---")
        print(program)
  
if __name__ == "__main__":
    main()
