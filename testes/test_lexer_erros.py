from lexer import Lexer
from tokens import TokenType

def testar_erros_lexer():
    # Cenários de Erro:
    # 1. Caracteres ilegais no início de variáveis (@, #, $)
    #    Nota: JS aceita $, mas sua especificação diz apenas letras e sublinhado.
    # 2. Caracteres especiais soltos que não são operadores (?, ~, ^)
    # 3. Identificadores "quebrados" por caracteres inválidos
    
    codigo_com_erros = """
    var @usuario = "Maria";
    let valor#total = 100;
    var desconto = 10%; 
    var teste = ?;
    """

    print("=== TESTE DE ROBUSTEZ DO LEXER (ERROS ESPERADOS) ===")
    print(f"Código Fonte:\n{codigo_com_erros}")
    print("-" * 50)

    lexer = Lexer(codigo_com_erros)
    
    erros_encontrados = 0
    token_count = 0

    while True:
        token = lexer.next_token()
        
        if token.type == TokenType.EOF:
            break
        
        token_count += 1
        
        # O Lexer foi programado para retornar UNKNOWN quando não reconhece algo
        if token.type == TokenType.UNKNOWN:
            print(f"🔴 [ERRO LÉXICO] Caractere inválido detectado: '{token.literal}'")
            erros_encontrados += 1
        else:
            print(f"🟢 Token Válido: {token}")

    print("-" * 50)
    print(f"Relatório Final:")
    print(f"Tokens processados: {token_count}")
    print(f"Erros encontrados: {erros_encontrados}")
    
    if erros_encontrados > 0:
        print("\n✅ SUCESSO: O Lexer identificou corretamente os caracteres inválidos!")
    else:
        print("\n❌ FALHA: O Lexer aceitou caracteres que deveriam ser inválidos.")

if __name__ == "__main__":
    testar_erros_lexer()