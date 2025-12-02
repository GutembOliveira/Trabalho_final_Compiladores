# semantic_analyzer.py

from parser import (
    Program, VarDecl, FuncDecl, ReturnStmt, IfStmt, Block, ExprStmt,
    Identifier, Literal, Unary, Binary, Assign, Call, Index, Node,
    ArrayLiteral # <<< NECESSÁRIO para inferir tipo de array
)

# -----------------------
# Tabela de Símbolos (Escopo)
# -----------------------
class Symbol:
    """Representa um símbolo (variável ou função) no código."""
    # NOVO: Adicionado 'type' = 'unknown', 'number', 'string', 'array', 'function', etc.
    def __init__(self, name: str, kind: str, mutable: bool, scope_type: str = 'var', type: str = 'unknown'):
        self.name = name
        self.kind = kind  # Ex: 'variable', 'function'
        self.mutable = mutable  # True para 'var'/'let', False para 'const'
        self.scope_type = scope_type # 'var', 'let', 'const'
        self.type = type # <<< NOVO: Tipo inferido

class SymbolTable:
    """Gerencia escopos aninhados para análise semântica."""
    def __init__(self, parent=None, scope_name="global", is_function_scope=False):
        self.symbols = {}
        self.parent = parent
        self.scope_name = scope_name
        self.is_function_scope = is_function_scope

    def define(self, symbol: Symbol):
        """Define um novo símbolo no escopo atual, verificando redeclaração."""
        if symbol.name in self.symbols:
            existing_sym = self.symbols[symbol.name]
            
            if existing_sym.scope_type in ('let', 'const') or symbol.scope_type in ('let', 'const'):
                return f"Erro Semântico: Identificador '{symbol.name}' já foi declarado como '{existing_sym.scope_type}' neste escopo."
            
            # Permite re-declaração de 'var' no escopo global ou de função (se for var/var)
            if existing_sym.scope_type == 'var' and symbol.scope_type == 'var' and not self.is_function_scope and self.parent is None:
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
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
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
        self.generic_visit(node)

    def visit_VarDecl(self, node: VarDecl):
        """Verifica declaração de variáveis (escopo, const) e infere tipo."""
        name = node.name.name
        kind = node.kind.lower() # 'var', 'let', 'const'
        mutable = (kind != 'const')
        scope_type = kind
        
        # 1. Visita o inicializador (útil para resolver identificadores usados no inicializador)
        self.visit(node.initializer)
        
        # 2. Inferência básica de Tipo (NOVO)
        inferred_type = 'unknown'
        if node.initializer:
            if isinstance(node.initializer, Literal):
                value = node.initializer.value
                # Assumindo que o valor de Literal já é o tipo nativo do Python
                if isinstance(value, (int, float)):
                    inferred_type = 'number'
                elif isinstance(value, str):
                    inferred_type = 'string'
            elif isinstance(node.initializer, ArrayLiteral):
                inferred_type = 'array'
            elif isinstance(node.initializer, Identifier):
                # Tenta copiar o tipo do símbolo já declarado
                resolved_symbol = self.current_scope.resolve(node.initializer.name)
                if resolved_symbol:
                    inferred_type = resolved_symbol.type
        
        # 3. Checagem de redeclaração e definição do Símbolo com o tipo
        new_symbol = Symbol(name, 'variable', mutable, scope_type, inferred_type) # PASSANDO O TIPO
        error_msg = self.current_scope.define(new_symbol)
        
        if error_msg:
            self._report_error(error_msg)
        
        # 4. Verifica se const tem inicializador
        if kind == 'const' and node.initializer is None:
            self._report_error(f"Erro Semântico: Variável 'const' '{name}' deve ser inicializada.")


    def visit_FuncDecl(self, node: FuncDecl):
        """Verifica declaração de funções (escopo e parâmetros)."""
        name = node.name.name
        
        # 1. Define o nome da função no escopo ATUAL (com tipo 'function')
        error_msg = self.current_scope.define(Symbol(name, 'function', True, 'var', 'function')) # TIPO 'function'
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
                # Parâmetros são tratados como 'let' com tipo 'unknown'
                self.current_scope.define(Symbol(param_name, 'variable', True, 'let', 'unknown'))
                param_names.add(param_name)
        
        # 4. Visita o corpo da função
        self.visit(node.body)
        
        # 5. Sai do escopo
        self._exit_scope()

    def visit_ReturnStmt(self, node: ReturnStmt):
        """Verifica se o return está em um escopo de função."""
        if self.in_function == 0:
            self._report_error("Erro Semântico: Declaração 'return' fora de uma função.")
        
        self.visit(node.value)

    def visit_IfStmt(self, node: IfStmt):
        """Visita a condição, o bloco then e o bloco else."""
        self.visit(node.condition)
        
        self._enter_scope("if-then-scope")
        self.visit(node.then_branch)
        self._exit_scope()
        
        if node.else_branch:
            self._enter_scope("if-else-scope")
            self.visit(node.else_branch)
            self._exit_scope()

    def visit_Block(self, node: Block):
        """Visita o corpo do bloco."""
        self.generic_visit(node)

    def visit_ExprStmt(self, node: ExprStmt):
        """Visita a expressão dentro do statement."""
        self.visit(node.expr)

    # --- Expressions ---
    
    def visit_Assign(self, node: Assign):
        """Verifica atribuição a constantes e declaração de variáveis (implicitamente)."""
        
        self.visit(node.value)
        
        if isinstance(node.left, Identifier):
            name = node.left.name
            symbol = self.current_scope.resolve(name)
            
            if symbol is None:
                self._report_error(f"Erro Semântico: Variável '{name}' não foi declarada antes de ser atribuída.")
            elif not symbol.mutable:
                self._report_error(f"Erro Semântico: Não é possível atribuir a constante '{name}'.")
        
        elif isinstance(node.left, Index):
            # Visita a coleção e o índice. O visit_Index fará a checagem de tipo.
            self.visit(node.left)
        else:
            self._report_error(f"Erro Semântico: Lado esquerdo de atribuição não é atribuível: {node.left.__class__.__name__}.")


    def visit_Identifier(self, node: Identifier):
        """Verifica se o identificador foi declarado."""
        name = node.name
        symbol = self.current_scope.resolve(name)
        
        if symbol is None:
            self._report_error(f"Erro Semântico: Uso de identificador '{name}' não declarado.")

    def visit_Binary(self, node: Binary):
        """Visita ambos os lados da expressão binária."""
        self.visit(node.left)
        self.visit(node.right)
        
    def visit_Unary(self, node: Unary):
        """Visita o lado direito da expressão unária."""
        self.visit(node.right)
        
    def visit_Call(self, node: Call):
        """Verifica se o callee é uma função e visita os argumentos."""
        
        self.visit(node.callee)
        
        if isinstance(node.callee, Identifier):
            callee_name = node.callee.name
            symbol = self.current_scope.resolve(callee_name)
            if symbol and symbol.kind != 'function':
                self._report_error(f"Aviso Semântico: Tentativa de chamar a variável '{callee_name}' que não é uma função conhecida.")
            elif symbol is None:
                # O erro de 'não declarado' já é capturado no visit_Identifier
                pass

        for arg in node.args:
            self.visit(arg)

    def visit_Index(self, node: Index):
        """Verifica se a coleção é indexável (NOVO) e visita o índice."""
        
        # 1. Visita a expressão da coleção (ex: Identifier 'myNum')
        self.visit(node.collection)
        
        # 2. Visita a expressão do índice (ex: Literal 0)
        self.visit(node.index)
        
        # 3. CHECAGEM DE TIPO PARA INDEXAÇÃO (NOVO)
        if isinstance(node.collection, Identifier):
            name = node.collection.name
            symbol = self.current_scope.resolve(name)
            
            if symbol:
                # Tipos permitidos para indexação em JS: 'array' e 'string'.
                if symbol.type not in ('array', 'string', 'unknown'):
                    self._report_error(f"Erro Semântico: A variável '{name}' do tipo '{symbol.type}' não é indexável. Acesso por índice inválido.")
            
    def visit_Literal(self, node: Literal):
        """Não faz nada em literais (terminal node)."""
        pass

    def visit_ArrayLiteral(self, node: ArrayLiteral):
        """Visita todos os elementos dentro do literal de array."""
        for element in node.elements:
            self.visit(element)