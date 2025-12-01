# Compilador para Linguagem Personalizada

## Descrição

Este projeto implementa um compilador completo para uma linguagem de programação personalizada. O compilador é dividido em duas partes principais:

- **Frontend**: Análise léxica e sintática (já implementado)
- **Backend**: Geração de código LLVM IR e compilação para executável

## Características da Linguagem

A linguagem suporta:

- Declarações de variáveis (`var`, `const`)
- Expressões aritméticas (`+`, `-`, `*`, `/`)
- Expressões lógicas (`&&`, `||`, `!`)
- Comparações (`<`, `>`, `<=`, `>=`, `==`, `!=`)
- Estruturas de controle (`if`/`else`)
- Funções (declaração básica)
- Comentários de linha (`//`)
- Tipos de dados: números, strings, booleanos

## Arquitetura do Compilador

### Frontend (Análise)

1. **Lexer** (`lexer.py`): Análise léxica - converte código fonte em tokens
2. **Parser** (`parser.py`): Análise sintática - converte tokens em AST (Abstract Syntax Tree)
3. **Tokens** (`tokens.py`): Definições dos tipos de tokens

### Backend (Síntese)

1. **Code Generator** (`codegen.py`): Geração de código LLVM IR a partir da AST
2. **Compiler** (`compile.py`): Script principal que coordena todo o processo

## Instalação de Pré-requisitos

### No Fedora 42

#### 1. Instalar Python e dependências básicas

```bash
# Atualizar sistema
sudo dnf update

# Instalar Python 3 e pip
sudo dnf install python3 python3-pip python3-devel

# Verificar instalação
python3 --version
pip3 --version
```

#### 2. Instalar LLVM e Clang

```bash
# Instalar LLVM e Clang
sudo dnf install llvm llvm-devel clang clang-devel

# Verificar instalação
llvm-config --version
clang --version
```

#### 3. Instalar dependências Python

```bash
# Instalar llvmlite (binding Python para LLVM)
pip3 install llvmlite

# Verificar instalação
python3 -c "import llvmlite; print('llvmlite instalado com sucesso')"
```

#### 4. Configurar variáveis de ambiente (se necessário)

```bash
# Adicionar ao ~/.bashrc ou ~/.zshrc se necessário
export LLVM_CONFIG=/usr/bin/llvm-config
```

### Instalação Alternativa via Conda (Recomendado)

Se você preferir usar conda para gerenciar dependências:

```bash
# Instalar miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Criar ambiente virtual
conda create -n compilador python=3.10
conda activate compilador

# Instalar dependências
conda install llvmlite -c conda-forge
conda install clang -c conda-forge
```

## Como Usar

### Compilação Básica

```bash
# Compilar um programa
python3 compile.py programa.txt

# Executar o programa compilado
./program
```

### Opções Avançadas

```bash
# Especificar nome do executável
python3 compile.py programa.txt -o meu_programa

# Mostrar tokens gerados
python3 compile.py programa.txt --tokens

# Mostrar árvore sintática (AST)
python3 compile.py programa.txt --ast

# Mostrar código LLVM IR gerado
python3 compile.py programa.txt --ir

# Só gerar IR, não compilar executável
python3 compile.py programa.txt --no-compile

# Ajuda
python3 compile.py --help
```

## Exemplos

### Exemplo 1: Programa com Sucesso

**Arquivo: `exemplo_sucesso.txt`**

```javascript
// Exemplo de programa válido
var x = 10;
var y = 5;
var resultado = x + y * 2;
if (resultado > 15) {
  var mensagem = "Resultado é maior que 15";
}
```

**Compilação:**

```bash
python3 compile.py exemplo_sucesso.txt -o exemplo_sucesso
./exemplo_sucesso
```

### Exemplo 2: Programa com Erro de Sintaxe

**Arquivo: `exemplo_erro.txt`**

```javascript
// Exemplo com erro de sintaxe
var x = 10
var y = ; // Erro: valor esperado após =
if x > 5) { // Erro: parêntese aberto faltando
    var z = 1;
}
```

**Compilação (com erro):**

```bash
python3 compile.py exemplo_erro.txt
```

**Saída esperada:**

```
Compilando arquivo: exemplo_erro.txt
==================================================
1. Análise Léxica...
2. Análise Sintática...

❌ ERROS DE PARSING:
  Erro sintático: esperado IDENT, encontrado SEMICOLON (em ;)
  Erro sintático: esperado LPAREN, encontrado IDENT (em x)
```

### Exemplo 3: Programa com Expressões Complexas

**Arquivo: `exemplo_complexo.txt`**

```javascript
// Programa com expressões mais complexas
var a = 5;
var b = 3;
var c = 2;

// Expressão aritmética complexa
var resultado = (a + b) * c - a / b;

// Expressões lógicas
var condicao = a > b && b > c;

if (condicao) {
  var final = resultado * 2;
} else {
  var final = resultado / 2;
}
```

## Estrutura do Projeto

```
Trabalho_final_Compiladores/
├── lexer.py              # Analisador léxico
├── parser.py             # Analisador sintático
├── tokens.py             # Definições de tokens
├── codegen.py            # Gerador de código LLVM
├── compile.py            # Script principal
├── main.py               # Script de teste (legacy)
├── source_code.txt       # Código fonte de exemplo
├── JavasplitLexer.tokens # Tokens ANTLR (legacy)
├── README.md             # Esta documentação
└── exemplos/             # Diretório com exemplos
    ├── exemplo_sucesso.txt
    ├── exemplo_erro.txt
    └── exemplo_complexo.txt
```

## Detalhes Técnicos

### Processo de Compilação

1. **Análise Léxica**: O lexer (`lexer.py`) lê o código fonte caractere por caractere e produz uma sequência de tokens.

2. **Análise Sintática**: O parser (`parser.py`) consome os tokens e constrói uma árvore sintática abstrata (AST) usando um parser recursivo descendente.

3. **Geração de Código**: O gerador de código (`codegen.py`) percorre a AST e produz código LLVM IR equivalente.

4. **Compilação Final**: O código LLVM IR é compilado para código objeto e depois linkado para produzir um executável usando o Clang.

### Tradução para LLVM IR

O backend implementa as seguintes traduções:

- **Variáveis**: Mapeadas para instruções `alloca` no stack
- **Expressões Aritméticas**: Traduzidas para instruções `fadd`, `fsub`, `fmul`, `fdiv`
- **Expressões Lógicas**: Traduzidas para instruções `fcmp`, `and`, `or`
- **Condicionais**: Traduzidas para instruções `br` (branch condicional)
- **Atribuições**: Traduzidas para instruções `store`
- **Literais**: Traduzidas para constantes LLVM

### Limitações Atuais

- Suporte limitado a funções definidas pelo usuário
- Apenas tipos numéricos (float64) como tipo principal
- Sem verificação de tipos rigorosa
- Sem otimizações avançadas

## Troubleshooting

### Erro: "llvmlite não encontrado"

```bash
pip3 install llvmlite
# ou
conda install llvmlite -c conda-forge
```

### Erro: "clang não encontrado"

```bash
sudo dnf install clang
```

### Erro: "LLVM development libraries não encontradas"

```bash
sudo dnf install llvm-devel
```

### Problemas de Permissão

```bash
# Tornar o executável executável
chmod +x programa

# Executar
./programa
```

## Resumo da Implementação

✅ **FRONTEND (Análise)**

- ✅ Analisador Léxico (Lexer) completo
- ✅ Analisador Sintático (Parser) recursivo descendente
- ✅ Geração de AST (Abstract Syntax Tree)
- ✅ Tratamento de erros léxicos e sintáticos
- ✅ Suporte a comentários (`//`)

✅ **BACKEND (Síntese)**

- ✅ Gerador de código LLVM IR funcional
- ✅ Tradução completa da AST para LLVM IR
- ✅ Compilação para executável usando Clang
- ✅ Suporte a todas as construções da linguagem

✅ **FUNCIONALIDADES IMPLEMENTADAS**

- ✅ Declarações de variáveis (`var`, `const`)
- ✅ Operações aritméticas (`+`, `-`, `*`, `/`)
- ✅ Operações lógicas (`&&`, `||`, `!`)
- ✅ Comparações (`<`, `>`, `<=`, `>=`, `==`, `!=`)
- ✅ Estruturas condicionais (`if`/`else`)
- ✅ Expressões com precedência correta
- ✅ Operadores unários (`-`, `!`)
- ✅ Atribuições e reatribuições
- ✅ Tipos: números, booleanos, strings

✅ **VALIDAÇÃO E TESTES**

- ✅ Exemplos com sucesso
- ✅ Exemplos com erros sintáticos
- ✅ Exemplos com erros semânticos
- ✅ Compilação e execução bem-sucedidas

## Teste Rápido

```bash
# 1. Ativar ambiente virtual
source .venv/bin/activate

# 2. Compilar exemplo simples
python compile.py exemplos/exemplo_simples.txt

# 3. Executar programa
./program

# 4. Ver todas as opções
python compile.py --help
```

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Teste thoroughly
5. Submeta um pull request

## Licença

Este projeto é desenvolvido para fins educacionais como trabalho final da disciplina de Compiladores.
