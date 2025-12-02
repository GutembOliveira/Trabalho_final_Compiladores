# Compilador com Backend LLVM

Este é um projeto de compilador desenvolvido como trabalho final da disciplina de Compiladores. Implementa um frontend (lexer + parser) para uma linguagem simples e um backend que gera código LLVM IR para compilação executável.

## 📋 Arquitetura do Compilador

### Frontend

- **Lexer** (`lexer.py`): Análise léxica que tokeniza o código fonte
- **Parser** (`parser.py`): Análise sintática que gera AST (Abstract Syntax Tree)
- **Tokens** (`tokens.py`): Definição de tipos de tokens e palavras-chave

### Backend

- **CodeGen** (`codegen.py`): Geração de código LLVM IR a partir da AST
- **Compile** (`compile.py`): Compilação final para executável usando clang

### Análise Semântica

- **Analyzer** (`analisadorSintatico.py`): Verificação de escopo, tipos e declarações

## 🛠️ Instalação de Bibliotecas Pré-requisitos

### Dependências Python

```bash
# Instalar llvmlite para geração de LLVM IR
pip install llvmlite

# Verificar versão instalada
python -c "import llvmlite; print(llvmlite.__version__)"
```

### Dependências do Sistema

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install clang llvm

# macOS com Homebrew
brew install llvm

# Verificar instalação
clang --version
llvm-config --version
```

## 🚀 Como Executar

### 1. Análise Completa (Lexer + Parser + Semântico)

```bash
python main.py
```

Este comando analisa o arquivo `source_code.txt` e executa todas as fases de análise.

### 2. Compilação para Executável

```bash
python compile.py
```

Este comando gera código LLVM IR e compila para executável.

### 3. Execução do Programa Compilado

```bash
./output  # Linux/macOS
output.exe  # Windows
```

## 📝 Exemplos de Código

### ✅ Exemplo de Código com Sucesso

**Arquivo: `examples/exemplo_sucesso_sem_print.txt`**

```javascript
// Programa simples que funciona corretamente
var x = 10;
var y = 20;
var resultado = x + y;

function soma(a, b) {
  return a + b;
}

var total = soma(x, y);

// Teste de condicionais
if (total > 25) {
  var mensagem = "maior";
} else {
  var mensagem2 = "menor";
}

// Teste de expressões complexas
var complexa = (x * 2 + y) / 5;
```

**Execução:**

```bash
# Copie o exemplo para o arquivo principal
cp examples/exemplo_sucesso_sem_print.txt source_code.txt
python main.py
```

**Saída esperada:**

```
--- 1. Análise Sintática ---
✅ Análise Sintática OK. AST gerada.

--- 2. Análise Semântica ---
✅ Análise Semântica OK. Não foram encontrados erros de escopo, atribuição, ou declaração.
```

### ❌ Exemplos de Código com Erros

#### Erro Léxico - Número Malformado

**Código:**

```javascript
var numero = 3.14.159;  // Erro: múltiplos pontos decimais
```

**Saída:**

```
--- 1. Análise Sintática ---
❌ ERROS SINTÁTICOS (PARSING)
Erro sintático: token prefixo inesperado UNKNOWN
```

#### Erro Sintático - Identificador Inválido

**Código:**

```javascript
var 123abc = 10;  // Erro: identificador não pode começar com número
```

**Saída:**

```
--- 1. Análise Sintática ---
❌ ERROS SINTÁTICOS (PARSING)
Erro sintático: esperado IDENT, encontrado NUMBER (em 123)
```

#### Erro Sintático - If sem Parênteses

**Código:**

```javascript
if x > 10 {  // Erro: missing parênteses na condição
    print(x);
}
```

**Saída:**

```
--- 1. Análise Sintática ---
❌ ERROS SINTÁTICOS (PARSING)
Erro sintático: esperado LPAREN, encontrado IDENT (em x)
```

#### Erro Semântico - Variável Não Declarada

**Código:**

```javascript
var x = 10;
var y = z + 5; // Erro: 'z' não foi declarada
```

**Saída:**

```
--- 2. Análise Semântica ---
⚠️ ERROS SEMÂNTICOS
Erro semântico: Variável 'z' não foi declarada antes do uso.
❌ Análise Semântica FALHOU com 1 erro(s).
```

### 🐛 Bugs e Limitações Conhecidas

### Problemas no Lexer

1. **Strings não fechadas são aceitas**: `"hello world` (sem aspas de fechamento)
2. **Números decimais malformados**: `3.14.159` gera tokens separados em vez de erro
3. **Caracteres especiais não tratados**: `@`, `#`, `$` não geram erro apropriado

### Problemas no Parser

1. **Operadores consecutivos**: `a + + b` não gera erro claro
2. **Expressões vazias**: `var x = ;` aceita atribuição vazia
3. **While não implementado**: Parser não reconhece loops `while`
4. **Recuperação de erro limitada**: Após erro, parsing pode ficar inconsistente

### Limitações Semânticas

1. **Função print não é built-in**: `print()` é tratada como função não declarada
2. **Sem verificação de tipos**: Aceita operações entre tipos incompatíveis
3. **Sem verificação de retorno**: Funções podem não retornar valores esperados

### Tokens Não Implementados

- **Operador módulo**: `%`
- **Operadores bitwise**: `&`, `|`, `^`
- **Loops**: `while`, `for`
- **Arrays avançados**: sintaxe `[1, 2, 3]`

## 🔧 Estrutura de Arquivos

```
Trabalho_final_Compiladores/
├── lexer.py              # Analisador léxico
├── parser.py             # Analisador sintático
├── tokens.py             # Definições de tokens
├── codegen.py            # Gerador de código LLVM
├── compile.py            # Compilador final
├── main.py               # Programa principal
├── analisadorSintatico.py # Análise semântica
├── source_code.txt       # Código fonte de teste
├── examples/             # Exemplos de código
│   ├── exemplo_sucesso_sem_print.txt
│   ├── exemplo_erro_lexico.txt
│   ├── exemplo_erro_sintatico.txt
│   └── exemplo_erro_semantico.txt
└── README.md             # Esta documentação
```

## 🎯 Funcionalidades Implementadas

### ✅ Suportado

- Declaração de variáveis (`var`, `const`)
- Funções com parâmetros e retorno
- Expressões aritméticas (`+`, `-`, `*`, `/`)
- Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Operadores lógicos (`&&`, `||`, `!`)
- Estruturas condicionais (`if`, `else`)
- Chamadas de função
- Análise semântica de escopo
- Geração de código LLVM IR
- Compilação para executável

### ❌ Não Implementado

- Loops (`while`, `for`)
- Arrays nativos
- Structs/Objects
- Imports/Modules
- Tratamento de exceções
- Garbage collection

## 🚀 Próximos Passos

1. **Melhorar tratamento de erros no lexer**

   - Validação rigorosa de números decimais
   - Verificação de strings não fechadas
   - Tratamento de caracteres inválidos

2. **Expandir funcionalidades do parser**

   - Implementar loops `while` e `for`
   - Melhorar recuperação de erros
   - Adicionar suporte a arrays

3. **Otimizações do backend**
   - Otimização de código LLVM
   - Melhor geração de código para expressões

## 👥 Autores

Trabalho desenvolvido para a disciplina de Compiladores - UFPI

### componentes

- Lucas matheus
- Gutemberg de Oliveira
- Ana carolina
