from lexer import Lexer
from tokens import TokenType

def testar_tokens():
    input_code = """
    var x = 10.5;
    console.log(x);
    let y = null;
    // Declaração de variáveis
    var x = 10;
    let y = 3.14;
    const name = "Thiago";

    // Função simples
    function greet(person) {
        return "Hello, " + person + "!";
    }

    // Condicional
    if (x > 5) {
        console.log(greet(name));
    } else {
        console.log("x is too small");
    }

    // Laço de repetição
    for (var i = 0; i < 3; i++) {
        console.log(i);
    }

    // Operadores lógicos
    var flag = true && false || !false;

    // Null e valores booleanos
    var z = null;
    var isActive = true;
    """
    
    print(f"Testando código:\n{input_code}")
    print("-" * 20)
    
    l = Lexer(input_code)
    
    while True:
        tok = l.next_token()
        print(tok)
        if tok.type == TokenType.EOF:
            break
            
if __name__ == "__main__":
    testar_tokens()