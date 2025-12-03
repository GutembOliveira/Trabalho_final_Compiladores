from lexer import Lexer
from parser import Parser
from analisadorSintatico import SemanticAnalyzer

def testar_erros_semanticos():
    # Este código contém PROPOSITALMENTE vários erros semânticos.
    # O objetivo é ver se o compilador pega todos eles.
    
    codigo_com_erros = """
    // 1. Erro: Variável não declarada
    x = 10; 
    
    // 2. Erro: Redeclaração de variável no mesmo escopo
    var a = 1;
    var a = 2; 
    
    // 3. Erro: Atribuição a constante
    const PI = 3.14;
    PI = 3.1415;
    
    // 4. Erro: Chamada de função com número errado de argumentos
    print("Olá", "Mundo"); // print espera 1, recebeu 2
    
    // 5. Erro: Tentar chamar algo que não é função
    var numero = 100;
    numero();
    
    // 6. Erro: Tentar indexar algo que não é array/string
    var simples = 10;
    var item = simples[0];
    
    // 7. Erro: Return fora de função
    return 0;
    
    function teste() {
        // 8. Erro: Variável fora de escopo (tentar usar algo de outro for/função fechada)
        // Isso é mais sutil, vamos testar o escopo do let
        if (true) {
            let bloco = "secreto";
        }
        print(bloco); // 'bloco' não existe aqui fora
    }
    """

    print("=== TESTE DE STRESS SEMÂNTICO (ERROS ESPERADOS) ===")
    print("-" * 50)

    # 1. Lexer
    lexer = Lexer(codigo_com_erros)
    
    # 2. Parser
    parser = Parser(lexer)
    program = parser.parse_program()
    
    # Se o Parser falhar (o que não deve acontecer, pois a sintaxe está ok), avisamos
    if len(parser.errors) > 0:
        print("❌ O teste falhou no PARSER (não deveria!):")
        for err in parser.errors: print(err)
        return

    # 3. Semântico
    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(program)

    print(f"Total de erros encontrados: {len(semantic_errors)}\n")
    
    if len(semantic_errors) > 0:
        print("🟢 O Analisador Semântico funcionou! Veja os erros barrados:")
        for i, erro in enumerate(semantic_errors, 1):
            print(f"  {i}. {erro}")
    else:
        print("🔴 FALHA GRAVE: O compilador aceitou código inválido!")

if __name__ == "__main__":
    testar_erros_semanticos()