// ✅ Exemplo 3: Programa com Funções
// Demonstra: declaração de função, parâmetros, return, chamadas

function somar(a, b) {
    var resultado = a + b;
    return resultado;
}

function multiplicar(x, y) {
    if (x == 0 || y == 0) {
        return 0;
    }
    return x * y;
}

// Chamadas de função
var soma = somar(10, 5);
var produto = multiplicar(4, 3);
var complexo = somar(produto, multiplicar(2, 3));