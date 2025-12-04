// 🔬 Exemplo ESPECÍFICO para demonstrar otimizações

function calculo_redundante(x) {
    var a = x * 2;      // Primeira multiplicação por 2
    var b = x + x;      // Segunda forma de multiplicar por 2 (redundante)
    var c = a + b;      // 4 * x (deveria ser otimizado)
    return c;
}

function loop_simples() {
    var total = 0;
    for (var i = 1; i <= 10; i = i + 1) {
        total = total + 1;  // Simplesmente conta de 1 a 10
    }
    return total;  // Sempre retorna 10 (pode ser otimizado para constante)
}

// Variáveis que podem ser otimizadas
var constante_calculada = 5 + 3;  // 8 (pode ser resolvido em tempo de compilação)
var resultado1 = calculo_redundante(5);  // 20
var resultado2 = loop_simples();          // 10
var resultado_final = constante_calculada + resultado1 + resultado2;