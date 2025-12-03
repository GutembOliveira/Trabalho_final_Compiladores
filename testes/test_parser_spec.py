from lexer import Lexer
from parser import Parser

def testar_especificacao_parser():
    # Código que usa TODAS as features implementadas:
    # 1. Variáveis (var, let, const) e Tipos (int, float, bool, string, array, null)
    # 2. Operadores (+, -, *, /, %, >, <, >=, <=, ==, !=, ===, !==, &&, ||, !)
    # 3. Estruturas (if/else, while, for)
    # 4. Funções (declaração dinâmica e chamadas)
    # 5. Arrays (acesso e métodos nativos simulados)
    
    codigo_fonte = """
    // 1. Declarações
    var x = 10;
    let pi = 3.1415;
    const nome = "Compilador";
    var ativo = true;
    var nulo = null;
    let lista = [1, 2, 3];

    // 2. Operadores e Precedência
    var resultado = (x + 5) * 2 > 20 && ativo == true;
    var estrito = 10 === "10";
    
    // 3. Funções (Dinâmicas)
    function calcular(a, b) {
        if (a > b) {
            return a - b;
        } else {
            return a + b;
        }
    }

    // 4. Chamadas e Acesso a Membros (console.log mantido)
    var res = calcular(10, 5);
    console.log(res);
    print("Resultado: " + res);

    // 5. Estruturas de Repetição
    
    // While
    var i = 0;
    while (i < 3) {
        push(lista, i);
        i = i + 1;
    }

    // For
    for (var j = 0; j < length(lista); j = j + 1) {
        var item = lista[j];
        if (item !== null) {
            println(item);
        }
    }
    """

    print("=== TESTE DO PARSER (ESPECIFICAÇÃO COMPLETA) ===")
    print("-" * 50)
    print(f"Código Fonte:\n{codigo_fonte}")
    print("-" * 50)

    lexer = Lexer(codigo_fonte)
    parser = Parser(lexer)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        print("❌ ERROS SINTÁTICOS ENCONTRADOS:")
        for erro in parser.errors:
            print(f"  - {erro}")
    else:
        print("✅ ANÁLISE SINTÁTICA BEM-SUCEDIDA!")
        print("\n=== AST GERADA (Estrutura da Árvore) ===")
        # Imprime cada statement da AST para facilitar a leitura
        for stmt in program.statements:
            print(stmt)

if __name__ == "__main__":
    testar_especificacao_parser()