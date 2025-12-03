from lexer import Lexer
from tokens import TokenType

def testar_especificacao_lexer():
    # Este código fonte reúne todos os elementos citados no PDF:
    # - Tipos: let, var, const, number, string, boolean
    # - Literais: Inteiros, Decimais (floats), Strings, Booleanos, Arrays
    # - Operadores: Aritméticos, Relacionais, Lógicos, Igualdade Restrita (===)
    # - Estruturas: if, else, while, for, function, return
    # - Funções Nativas: print, input, length, push, etc.
    
    codigo_fonte_spec = """
    // === 1. Tipos Básicos e Declarações (PDF pág. 2 e 3) ===
    let idade = 24;           // Inteiro
    var altura = 1.58;        // Float (Decimal)
    const PI = 3.1415;        // Constante
    let nome = "Ana";         // String
    let ativo = true;         // Boolean (true)
    let inativo = false;      // Boolean (false)
    let lista = ["A", "B"];   // Array Literal

    // === 2. Operadores e Precedência (PDF pág. 2) ===
    // Matemáticos
    var calc = (10 + 5) * 2 / 4 - 1;
    
    // Relacionais e Lógicos
    // Testando tokens complexos: >=, <=, ==, !=, ===, !==, &&, ||
    if (idade >= 18 && (altura < 2.0 || ativo == true)) {
        var teste1 = 10 === "10"; // Igualdade estrita
        var teste2 = 10 !== "10"; // Desigualdade estrita
    }

    // === 3. Funções e Estruturas de Controle (PDF pág. 3 a 8) ===
    
    // Declaração de Função (Sintaxe dinâmica adotada)
    function processarDados(dado) {
        if (!dado) {
            return void; // Token VOID
        }
        return dado;
    }

    // Estruturas de Repetição
    var contador = 0;
    while (contador < 5) {
        contador = contador + 1;
    }

    for (let i = 0; i < 10; i = i + 1) {
        // === 4. Funções Nativas Específicas (PDF pág. 4 e 5) ===
        // O lexer deve reconhecer estes nomes como IDENT
        print(i);
        println("Texto");
        var entrada = input();
        var num = toNumber(entrada);
        var tam = length(lista);
        push(lista, num);
        pop(lista);
        var texto = concat("Olá", " Mundo");
    }
    """

    print("=== INICIANDO TESTE DO LEXER (BASEADO NA ESPECIFICAÇÃO) ===\n")
    
    lexer = Lexer(codigo_fonte_spec)
    
    token_count = 0
    while True:
        token = lexer.next_token()
        
        # Formatação para facilitar a leitura no terminal
        print(f"{str(token_count).zfill(3)} | {token}")
        
        token_count += 1
        if token.type == TokenType.EOF:
            break
            
    print(f"\n=== FIM DO TESTE. Total de tokens: {token_count} ===")

if __name__ == "__main__":
    testar_especificacao_lexer()