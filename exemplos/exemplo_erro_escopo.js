// ❌ Exemplo 7: Programa com Erro de Escopo
// Demonstra erros relacionados a escopo de variáveis

function minhaFuncao() {
    let localVar = 42;
    
    if (true) {
        let blocoVar = 10;
        var funcVar = 20;
    }
    
    // ERRO: blocoVar não existe neste escopo
    return blocoVar + localVar;
}

// ERRO: return fora de função
return 10;

// ERRO: Uso de variável de função fora dela
var teste = localVar;