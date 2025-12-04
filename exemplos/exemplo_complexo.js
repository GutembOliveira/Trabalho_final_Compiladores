// ✅ Exemplo 8: Programa Complexo Completo
// Demonstra: múltiplas funcionalidades integradas

// Função para calcular factorial
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Função para verificar se é par
function ehPar(numero) {
    return numero % 2 == 0;
}

// Programa principal
const limite = 5;
var soma = 0;

for (let i = 1; i <= limite; i = i + 1) {
    let fat = factorial(i);
    
    if (ehPar(i)) {
        soma = soma + fat;
    } else {
        soma = soma - fat;
    }
}

// Resultado final
var resultado = soma > 0;