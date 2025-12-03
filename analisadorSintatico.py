# analisadorSintatico.py

from parser import (
    Program, VarDecl, FuncDecl, ReturnStmt, IfStmt, Block, ExprStmt,
    Identifier, Literal, Unary, Binary, Assign, Call, Index, Node,
    ArrayLiteral, WhileStmt, ForStmt
)

# -----------------------
# Tabela de Símbolos (Escopo)
# -----------------------
class Symbol:
    """Representa um símbolo (variável ou função) no código."""
    def __init__(self, name: str, kind: str, mutable: bool, scope_type: str = 'var', type: str = 'unknown', params: list = None, return_type: str = None):
        self.name = name
        self.kind = kind  # Ex: 'variable', 'function'
        self.mutable = mutable  # True para 'var'/'let', False para 'const'
        self.scope_type = scope_type # 'var', 'let', 'const'
        self.type = type # Tipo inferido
        self.params = params if params else [] # Lista de tipos esperados
        self.return_type = return_type         # Tipo de retorno

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
        self._define_native_functions()
        self.current_scope = self.global_scope
        self.in_function = 0

    def _define_native_functions(self):
        """Define as funções nativas especificadas no Trabalho Final."""
        natives = [
            ("print",    ["string"], "void"),
            ("println",  ["string"], "void"),
            ("input",    [],         "string"),
            ("toNumber", ["string"], "number"),
            ("length",   ["any"],    "number"), 
            ("push",     ["array", "any"], "void"),
            ("pop",      ["array"],  "any"),
            ("concat",   ["string", "string"], "string")
        ]

        for name, params, ret_type in natives:
            sym = Symbol(
                name=name, 
                kind='function', 
                mutable=False, 
                scope_type='global', 
                type='function',
                params=params, 
                return_type=ret_type
            )
            self.global_scope.define(sym)

    def _enter_scope(self, scope_name="block", is_function_scope=False):
        new_scope = SymbolTable(parent=self.current_scope, scope_name=scope_name, is_function_scope=is_function_scope)
        self.current_scope = new_scope
        if is_function_scope:
            self.in_function += 1

    def _exit_scope(self):
        if self.current_scope.is_function_scope:
            self.in_function -= 1
        self.current_scope = self.current_scope.parent

    def _report_error(self, msg: str, node: Node = None):
        self.errors.append(msg)

    def analyze(self, ast: Program):
        self.visit_Program(ast)
        return self.errors

    # -------------------
    # Visitor pattern
    # -------------------

    def visit(self, node):
        if node is None:
            return
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
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
        
    # --- Visitors ---
    
    def visit_Program(self, node: Program):
        self.generic_visit(node)

    def visit_VarDecl(self, node: VarDecl):
        name = node.name.name
        kind = node.kind.lower()
        mutable = (kind != 'const')
        
        self.visit(node.initializer)
        
        inferred_type = 'unknown'
        if node.initializer:
            if isinstance(node.initializer, Literal):
                value = node.initializer.value
                if isinstance(value, (int, float)): inferred_type = 'number'
                elif isinstance(value, str): inferred_type = 'string'
            elif isinstance(node.initializer, ArrayLiteral):
                inferred_type = 'array'
            elif isinstance(node.initializer, Identifier):
                resolved = self.current_scope.resolve(node.initializer.name)
                if resolved: inferred_type = resolved.type
        
        new_symbol = Symbol(name, 'variable', mutable, kind, inferred_type)
        error_msg = self.current_scope.define(new_symbol)
        
        if error_msg:
            self._report_error(error_msg)
        
        if kind == 'const' and node.initializer is None:
            self._report_error(f"Erro Semântico: Variável 'const' '{name}' deve ser inicializada.")

    def visit_FuncDecl(self, node: FuncDecl):
        name = node.name.name
        # Tipagem dinâmica: assumimos 'any' para todos os parâmetros
        param_types = ['any'] * len(node.params)
        
        func_symbol = Symbol(
            name=name, kind='function', mutable=True, scope_type='var', 
            type='function', params=param_types, return_type='any'
        )
        
        error_msg = self.current_scope.define(func_symbol)
        if error_msg:
            self._report_error(error_msg)
            
        self._enter_scope(scope_name=f"function:{name}", is_function_scope=True)
        
        param_names = set()
        for param in node.params:
            param_name = param.name
            if param_name in param_names:
                self._report_error(f"Erro Semântico: Parâmetro '{param_name}' duplicado na função '{name}'.")
            else:
                self.current_scope.define(Symbol(param_name, 'variable', True, 'let', 'any'))
                param_names.add(param_name)
        
        self.visit(node.body)
        self._exit_scope()

    def visit_ReturnStmt(self, node: ReturnStmt):
        if self.in_function == 0:
            self._report_error("Erro Semântico: Declaração 'return' fora de uma função.")
        self.visit(node.value)

    def visit_IfStmt(self, node: IfStmt):
        self.visit(node.condition)
        self._enter_scope("if-then-scope")
        self.visit(node.then_branch)
        self._exit_scope()
        if node.else_branch:
            self._enter_scope("if-else-scope")
            self.visit(node.else_branch)
            self._exit_scope()

    def visit_WhileStmt(self, node: WhileStmt):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ForStmt(self, node: ForStmt):
        # Cria escopo para a inicialização (ex: let i=0)
        self._enter_scope("for-loop")
        
        if node.init:
            self.visit(node.init) # Agora visitamos normalmente, pois node.init é VarDecl
            
        if node.condition:
            self.visit(node.condition)
            
        if node.increment:
            self.visit(node.increment)
            
        self.visit(node.body)
        self._exit_scope()

    def visit_Block(self, node: Block):
        self.generic_visit(node)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_Assign(self, node: Assign):
        self.visit(node.value)
        if isinstance(node.left, Identifier):
            name = node.left.name
            symbol = self.current_scope.resolve(name)
            if symbol is None:
                self._report_error(f"Erro Semântico: Variável '{name}' não foi declarada antes de ser atribuída.")
            elif not symbol.mutable:
                self._report_error(f"Erro Semântico: Não é possível atribuir a constante '{name}'.")
        elif isinstance(node.left, Index):
            self.visit(node.left)
        else:
            self._report_error(f"Erro Semântico: Lado esquerdo inválido na atribuição.")

    def visit_Identifier(self, node: Identifier):
        name = node.name
        symbol = self.current_scope.resolve(name)
        if symbol is None:
            self._report_error(f"Erro Semântico: Uso de identificador '{name}' não declarado.")

    def visit_Binary(self, node: Binary):
        self.visit(node.left)
        self.visit(node.right)
        
    def visit_Unary(self, node: Unary):
        self.visit(node.right)
        
    def visit_Call(self, node: Call):
        callee_name = None
        func_symbol = None

        if isinstance(node.callee, Identifier):
            callee_name = node.callee.name
            func_symbol = self.current_scope.resolve(callee_name)
            
            if func_symbol is None:
                self._report_error(f"Erro Semântico: Função '{callee_name}' não foi declarada.")
                return 
            elif func_symbol.kind != 'function':
                self._report_error(f"Erro Semântico: '{callee_name}' não é uma função.")
                return

        for arg in node.args:
            self.visit(arg)

        # Validação de Assinatura (Contagem de argumentos)
        if func_symbol:
            expected_params = func_symbol.params
            received_args = node.args
            if len(received_args) != len(expected_params):
                self._report_error(f"Erro Semântico: Função '{callee_name}' espera {len(expected_params)} argumentos, mas recebeu {len(received_args)}.")

    def visit_Index(self, node: Index):
        self.visit(node.collection)
        self.visit(node.index)
        if isinstance(node.collection, Identifier):
            name = node.collection.name
            symbol = self.current_scope.resolve(name)
            if symbol and symbol.type not in ('array', 'string', 'unknown'):
                self._report_error(f"Erro Semântico: A variável '{name}' do tipo '{symbol.type}' não é indexável.")
            
    def visit_Literal(self, node: Literal):
        pass

    def visit_ArrayLiteral(self, node: ArrayLiteral):
        for element in node.elements:
            self.visit(element)