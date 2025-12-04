// ✅ Exemplo Intensivo para Demonstrar Otimizações
// Demonstra: operações redundantes e loops que podem ser otimizados

// Função com cálculos redundantes (candidata a otimização)
function calculos_redundantes(x) {
    var a = x * 2;
    var b = x * 2;  // Redundante - mesmo cálculo de 'a'
    var c = a + b;   // 4 * x
    var d = x + x + x + x;  // Também 4 * x - redundante com 'c'
    return c + d;    // 8 * x
}

// Função com loop simples
function soma_sequencial(limite) {
    var total = 0;
    for (var i = 1; i <= limite; i = i + 1) {
        total = total + i;
    }
    return total;
}

// Função que deveria ser inline-able em O3
function operacao_simples(a, b) {
    return a + b;
}

// Função com múltiplas chamadas da função simples
function multiplas_operacoes() {
    var x = 10;
    var y = 20;
    
    // Essas chamadas podem ser inline-adas em O3
    var resultado1 = operacao_simples(x, y);
    var resultado2 = operacao_simples(resultado1, 5);
    var resultado3 = operacao_simples(resultado2, x);
    
    return resultado3;
}

// Programa principal com vários cálculos
var limite = 100;
var resultado_soma = soma_sequencial(limite);
var resultado_redundante = calculos_redundantes(15);
var resultado_multiplo = multiplas_operacoes();

// Operações adicionais que podem ser otimizadas
var constante1 = 5 * 10;  // Pode ser dobrado em tempo de compilação
var constante2 = 50;       // Redundante com constante1
var constante3 = constante1 + 0;  // Operação desnecessária

var resultado_final = resultado_soma + resultado_redundante + resultado_multiplo;