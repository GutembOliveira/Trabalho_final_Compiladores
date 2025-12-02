# semantic_analyzer.py

from parser import (
    Program, VarDecl, FuncDecl, ReturnStmt, IfStmt, Block, ExprStmt,
    Identifier, Literal, Unary, Binary, Assign, Call, Index, Node
)

# -----------------------
# Tabela de Símbolos (Escopo)
# -----------------------
class Symbol:
    """Representa um símbolo (variável ou função) no código."""
    def __init__(self, name: str, kind: str, mutable: bool, scope_type: str = 'var'):
        self.name = name
        self.kind = kind  # Ex: 'variable', 'function'
        self.mutable = mutable  # True para 'var'/'let', False para 'const'
        self.scope_type = scope_type # 'var', 'let', 'const'

class SymbolTable:
    """Gerencia escopos aninhados para análise semântica."""
    def __init__(self, parent=None, scope_name="global", is_function_scope=False):
        self.symbols = {}
        self.parent = parent
        self.scope_name = scope_name
        self.is_function_scope = is_function_scope # Indica se este escopo é de uma função (necessário para 'return')

    def define(self, symbol: Symbol):
        """Define um novo símbolo no escopo atual, verificando redeclaração."""
        if symbol.name in self.symbols:
            # Regra JS: 'let'/'const' não pode ser redeclarado no mesmo escopo
            existing_sym = self.symbols[symbol.name]
            
            if existing_sym.scope_type in ('let', 'const') or symbol.scope_type in ('let', 'const'):
                 # Redeclaração ilegal (let/const tenta redeclarar let/const ou var tenta redeclarar let/const)
                return f"Erro Semântico: Identificador '{symbol.name}' já foi declarado como '{existing_sym.scope_type}' neste escopo."
            
            # Se for 'var' em escopo não de bloco, geralmente permite (com hoisting), 
            # mas simplificamos para:
            if existing_sym.scope_type == 'var' and symbol.scope_type == 'var' and not self.is_function_scope and self.parent is None:
                # Permite re-declaração de 'var' no escopo global ou de função (sem erro, mas pode ser avisado)
                pass
            else:
                 return f"Erro Semântico: Identificador '{symbol.name}' já foi declarado neste escopo."
            
        self.symbols[symbol.name] = symbol
        return None

    def resolve(self, name: str) -> Symbol | None:
        """Busca um símbolo, subindo na cadeia de escopo."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

    def resolve_current_scope(self, name: str) -> Symbol | None:
        """Busca um símbolo APENAS no escopo atual."""
        return self.symbols.get(name)

# -----------------------
# Analisador Semântico
# -----------------------
class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.global_scope = SymbolTable(scope_name="global")
        self.current_scope = self.global_scope
        self.in_function = 0 # Contador para saber se estamos dentro de uma função

    def _enter_scope(self, scope_name="block", is_function_scope=False):
        """Entra em um novo escopo."""
        new_scope = SymbolTable(parent=self.current_scope, scope_name=scope_name, is_function_scope=is_function_scope)
        self.current_scope = new_scope
        if is_function_scope:
            self.in_function += 1

    def _exit_scope(self):
        """Sai do escopo atual."""
        if self.current_scope.is_function_scope:
            self.in_function -= 1
        self.current_scope = self.current_scope.parent

    def _report_error(self, msg: str, node: Node = None):
        """Registra um erro semântico."""
        # Poderia incluir linha/coluna se o AST armazenasse essa informação
        self.errors.append(msg)

    def analyze(self, ast: Program):
        """Inicia a análise semântica da AST."""
        self.visit_Program(ast)
        return self.errors

    # -------------------
    # Visitor pattern para a AST
    # -------------------

    def visit(self, node):
        """Método de dispatch genérico."""
        if node is None:
            return
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Visitante padrão para nós não implementados ou simples."""
        # Se for um nó de lista, itera (ex: Block, Program)
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
        # Se for nó com filhos, visita explicitamente (útil para expressions)
        elif hasattr(node, '__dict__'):
            for attr, child in node.__dict__.items():
                if isinstance(child, Node):
                    self.visit(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, Node):
                            self.visit(item)
        
    # --- Statements ---
    
    def visit_Program(self, node: Program):
        """Visita o nó raiz."""
        # Programa global já usa o self.global_scope
        self.generic_visit(node)

    def visit_VarDecl(self, node: VarDecl):
        """Verifica declaração de variáveis (escopo e const)."""
        name = node.name.name
        kind = node.kind.lower() # 'var', 'let', 'const'
        mutable = (kind != 'const')
        scope_type = kind
        
        # 1. Checagem de redeclaração
        error_msg = self.current_scope.define(Symbol(name, 'variable', mutable, scope_type))
        if error_msg:
            self._report_error(error_msg)
        
        # 2. Verifica se const tem inicializador (regra JS: const deve ser inicializado)
        if kind == 'const' and node.initializer is None:
            self._report_error(f"Erro Semântico: Variável 'const' '{name}' deve ser inicializada.")

        # 3. Visita o inicializador
        self.visit(node.initializer)

    def visit_FuncDecl(self, node: FuncDecl):
        """Verifica declaração de funções (escopo e parâmetros)."""
        name = node.name.name
        
        # 1. Define o nome da função no escopo ATUAL (mesmo que 'var' em JS)
        error_msg = self.current_scope.define(Symbol(name, 'function', True, 'var'))
        if error_msg:
            self._report_error(error_msg)
            
        # 2. Entra no escopo da função para parâmetros e corpo
        self._enter_scope(scope_name=f"function:{name}", is_function_scope=True)
        
        # 3. Define parâmetros no novo escopo
        param_names = set()
        for param in node.params:
            param_name = param.name
            if param_name in param_names:
                self._report_error(f"Erro Semântico: Parâmetro '{param_name}' duplicado na função '{name}'.")
            else:
                # Parâmetros são tratados como 'let' (imutáveis a nível de redeclaração de nome)
                self.current_scope.define(Symbol(param_name, 'variable', True, 'let'))
                param_names.add(param_name)
        
        # 4. Visita o corpo da função
        self.visit(node.body)
        
        # 5. Sai do escopo
        self._exit_scope()

    def visit_ReturnStmt(self, node: ReturnStmt):
        """Verifica se o return está em um escopo de função."""
        if self.in_function == 0:
            self._report_error("Erro Semântico: Declaração 'return' fora de uma função.")
        
        # Visita o valor de retorno, se houver
        self.visit(node.value)

    def visit_IfStmt(self, node: IfStmt):
        """Visita a condição, o bloco then e o bloco else."""
        # 1. Visita a condição (deve ser avaliável)
        self.visit(node.condition)
        
        # 2. Visita o bloco then (cria escopo de bloco)
        self._enter_scope("if-then-scope")
        self.visit(node.then_branch)
        self._exit_scope()
        
        if node.else_branch:
            # 3. Visita o bloco else (cria escopo de bloco)
            self._enter_scope("if-else-scope")
            self.visit(node.else_branch)
            self._exit_scope()

    def visit_Block(self, node: Block):
        """Visita o corpo do bloco."""
        # O gerenciamento de escopo é feito pelo caller (FuncDecl, IfStmt, etc.)
        self.generic_visit(node)

    def visit_ExprStmt(self, node: ExprStmt):
        """Visita a expressão dentro do statement."""
        self.visit(node.expr)

    # --- Expressions ---
    
    def visit_Assign(self, node: Assign):
        """Verifica atribuição a constantes e declaração de variáveis (implicitamente)."""
        
        # Lado direito: deve ser visitado para checar uso de identificadores
        self.visit(node.value)
        
        # Lado esquerdo: deve ser um identificador ou um acesso de índice
        if isinstance(node.left, Identifier):
            name = node.left.name
            symbol = self.current_scope.resolve(name)
            
            if symbol is None:
                # Atribuição a variável não declarada (JS cria variável global se não estiver em 'strict mode')
                # Aqui, consideramos um erro (comportamento de 'strict mode' preferível para análise estática).
                self._report_error(f"Erro Semântico: Variável '{name}' não foi declarada antes de ser atribuída.")
            elif not symbol.mutable:
                # Reatribuição a 'const'
                self._report_error(f"Erro Semântico: Não é possível atribuir a constante '{name}'.")
        
        elif isinstance(node.left, Index):
            # Atribuição a item de coleção. Checamos se a coleção foi declarada.
            self.visit(node.left.collection)
            self.visit(node.left.index)
        else:
            self._report_error(f"Erro Semântico: Lado esquerdo de atribuição não é atribuível: {node.left.__class__.__name__}.")


    def visit_Identifier(self, node: Identifier):
        """Verifica se o identificador foi declarado."""
        name = node.name
        symbol = self.current_scope.resolve(name)
        
        if symbol is None:
            # Em JS, usar uma variável não declarada resulta em ReferenceError
            self._report_error(f"Erro Semântico: Uso de identificador '{name}' não declarado.")
            
        # Opcionalmente, anexa o símbolo ao nó para uso posterior.
        # node.symbol = symbol

    def visit_Binary(self, node: Binary):
        """Visita ambos os lados da expressão binária."""
        self.visit(node.left)
        self.visit(node.right)
        
        # Em análise de tipos, a verificação de compatibilidade seria feita aqui.

    def visit_Unary(self, node: Unary):
        """Visita o lado direito da expressão unária."""
        self.visit(node.right)
        
    def visit_Call(self, node: Call):
        """Verifica se o callee é uma função e visita os argumentos."""
        
        # 1. Visita o callee para garantir que ele é conhecido
        self.visit(node.callee)
        
        # 2. Se o callee for um Identificador, verifica se é uma função (melhor esforço)
        if isinstance(node.callee, Identifier):
            callee_name = node.callee.name
            symbol = self.current_scope.resolve(callee_name)
            if symbol and symbol.kind != 'function':
                self._report_error(f"Aviso Semântico: Tentativa de chamar a variável '{callee_name}' que não é uma função conhecida.")
            elif symbol is None:
                # Erro de variável não declarada (se não for pego no visit_Identifier)
                pass

        # 3. Visita os argumentos
        for arg in node.args:
            self.visit(arg)

    def visit_Index(self, node: Index):
        """Visita a coleção e o índice."""
        self.visit(node.collection)
        self.visit(node.index)

    def visit_Literal(self, node: Literal):
        """Não faz nada em literais (terminal node)."""
        pass