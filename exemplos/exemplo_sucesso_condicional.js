// ✅ Exemplo 2: Programa com Condicionais
// Demonstra: if/else, comparações, variáveis let/const

let idade = 25;
const maioridade = 18;

if (idade >= maioridade) {
    var status = "adulto";
    let categoria = 1;
} else {
    var status = "menor";
    let categoria = 0;
}

// Teste de operadores lógicos
var temPermissao = idade >= 18 && idade <= 65;
var precisaAutorizacao = !temPermissao;