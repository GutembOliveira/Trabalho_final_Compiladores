from lexer import Lexer
from parser import Parser
from analisadorSintatico import SemanticAnalyzer

def testar_semantico_pdf():
    # O mesmo código da especificação que o Parser aceitou
    codigo_fonte = """
    // 1. Variáveis
    let idade = 24;
    const PI = 3.1415;
    let nome = "Ana";
    let lista = ["A", "B", "C"];

    // 2. Funções Nativas (Agora o Semântico deve reconhecer estas funções!)
    print("Olá");
    
    // input() retorna string. toNumber recebe string. Isso é válido.
    var entrada = input();
    var num = toNumber(entrada);
    
    // length aceita array.
    var tamanho = length(lista);
    
    // push aceita array e any.
    push(lista, "D");
    
    // 3. Estruturas de Controle e Escopos
    if (tamanho > 0) {
        println("Lista não vazia");
    } else {
        println("Lista vazia");
    }

    var contador = 0;
    while (contador < 5) {
        // contador deve ser resolvido no escopo acima
        print(contador);
        contador = contador + 1;
    }

    // FOR: 'i' é declarado no escopo do loop
    for (let i = 0; i < 10; i = i + 1) {
        print(i);
    }
    
    // 4. Declaração de Função
    function somar(a, b) {
        return a + b;
    }
    
    var resultado = somar(10, 20);
    """

    print("=== TESTE DO ANALISADOR SEMÂNTICO (ESPECIFICAÇÃO) ===")
    print("Verificando se as funções nativas e escopos são reconhecidos...")
    print("-" * 50)

    # 1. Lexer
    lexer = Lexer(codigo_fonte)
    
    # 2. Parser
    parser = Parser(lexer)
    program = parser.parse_program()
    
    if len(parser.errors) > 0:
        print("❌ Erro no Parser (Isso não deveria acontecer pois já testamos):")
        for err in parser.errors: print(err)
        return

    # 3. Semântico
    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(program)

    if len(semantic_errors) > 0:
        print("❌ ERROS SEMÂNTICOS ENCONTRADOS:")
        for erro in semantic_errors:
            print(f"  - {erro}")
        print("\n[Diagnóstico]: Se o erro for 'Função print não declarada', verifique se você atualizou o analisadorSintatico.py com o método _define_native_functions.")
    else:
        print("✅ SUCESSO TOTAL: O código da especificação passou na Análise Semântica!")
        print("Isso prova que:")
        print("  1. As funções nativas (print, input, etc.) estão registradas.")
        print("  2. Os escopos (if, while, for) estão funcionando.")
        print("  3. Não há variáveis não declaradas.")

if __name__ == "__main__":
    testar_semantico_pdf()