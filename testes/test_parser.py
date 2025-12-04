from lexer import Lexer
from parser import Parser

def testar_parser():
    input_code = """
                    console.log(10);
                    var x = 10;
                let y = 3.14;
                const name = "Thiago";

                // Função simples
                function greet(person) {
                    if (person === null) {
                        return "Hello, stranger!";
                    } else {
                        return "Hello, " + person + "!";
                    }
                }

                // Chamando a função
                var message = greet(name);
                console.log(message);

                // Loop for
                for (var i = 0; i < 3; i = i + 1) {
                    console.log(i);
                }

                // While loop
                var counter = 0;
                while (counter < 2) {
                    console.log(counter);
                    counter = counter + 1;
                }

                // Operadores lógicos e booleanos
                var flag = true && false || !false;
                var isActive = true;
                var nothing = null;
    """
    
    print(f"Testando Parser com: {input_code}")
    print("-" * 30)
    
    lexer = Lexer(input_code)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    if len(parser.errors) > 0:
        print("❌ Erros encontrados:")
        for err in parser.errors:
            print(err)
    else:
        print("✅ Parsing Sucesso!")
        print(program)
        # Esperado algo como: Program([ExprStmt(Call(MemberExpr(Id(console), Id(log)), [Lit(10.0)]))])

if __name__ == "__main__":
    testar_parser()