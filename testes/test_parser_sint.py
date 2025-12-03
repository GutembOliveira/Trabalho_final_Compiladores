from lexer import Lexer
from parser import Parser

def testar_sintatico_pdf():
    # Exemplos baseados no PDF "Trabalho Final.pdf"
    codigo_fonte = """
    // 1. Variáveis (Pág. 2)
    let idade = 24;
    const PI = 3.1415;
    let nome = "Ana";
    let lista = ["A", "B", "C"];

    // 2. Funções Nativas (Pág. 4 e 5)
    // Para o Parser, isso são apenas chamadas de função normais (CallExpression)
    print("Olá");
    var entrada = input();
    var num = toNumber(entrada);
    var tamanho = length(lista);
    push(lista, "D");
    
    // 3. Estruturas de Controle (Pág. 6, 7 e 8)
    
    // IF / ELSE
    if (tamanho > 0) {
        println("Lista não vazia");
    } else {
        println("Lista vazia");
    }

    // WHILE
    var contador = 0;
    while (contador < 5) {
        print(contador);
        contador = contador + 1;
    }

    // FOR (Pág. 8) - Testando inicialização com 'let'
    for (let i = 0; i < 10; i = i + 1) {
        print(i);
    }
    
    // 4. Declaração de Função (Tipagem Dinâmica conforme sua escolha)
    function somar(a, b) {
        return a + b;
    }
    """

    print("=== TESTE EXCLUSIVO DO ANALISADOR SINTÁTICO ===")
    print("Verificando se o Parser aceita as estruturas do PDF...")
    print("-" * 50)

    lexer = Lexer(codigo_fonte)
    parser = Parser(lexer)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        print("❌ FALHA: Erros Sintáticos Encontrados:")
        for erro in parser.errors:
            print(f"  - {erro}")
    else:
        print("✅ SUCESSO: O Parser aceitou todo o código da especificação!")
        print("\n--- Estrutura da AST Gerada (Resumo) ---")
        for stmt in program.statements:
            # Imprime o tipo da classe do nó para confirmar que foi reconhecido
            nome_classe = stmt.__class__.__name__
            
            # Detalhes extras dependendo do tipo
            detalhe = ""
            if nome_classe == 'VarDecl':
                detalhe = f" -> {stmt.name.name}"
            elif nome_classe == 'FuncDecl':
                detalhe = f" -> {stmt.name.name}"
            elif nome_classe == 'ExprStmt':
                if hasattr(stmt.expr, 'callee'): # É uma chamada de função?
                     detalhe = f" -> Chamada de '{stmt.expr.callee.name}'"
            
            print(f"[{nome_classe}]{detalhe}")

if __name__ == "__main__":
    testar_sintatico_pdf()