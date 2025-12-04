// ✅ Exemplo 4: Programa com Loops
// Demonstra: while, for, escopo de variáveis

var contador = 0;
while (contador < 5) {
    var temp = contador * 2;
    contador = contador + 1;
}

for (let i = 0; i < 3; i = i + 1) {
    var valor = i + 10;
    let local = valor * 2;
}

// Teste de escopo
var global = 100;