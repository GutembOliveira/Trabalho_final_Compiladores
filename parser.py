# parser.py
from tokens import TokenType
from lexer import Lexer

# -----------------------
# AST nodes (simples, só para análise e depuração)
# -----------------------
class Node:
    pass

class Program(Node):
    def __init__(self, statements=None):
        self.statements = statements if statements is not None else []
    def __repr__(self):
        return f"Program({self.statements})"

class VarDecl(Node):
    def __init__(self, kind, name, initializer):
        self.kind = kind        # 'var' | 'let' | 'const'
        self.name = name        # Identifier
        self.initializer = initializer
    def __repr__(self):
        return f"VarDecl({self.kind}, {self.name}, {self.initializer})"

class FuncDecl(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body  # Block
    def __repr__(self):
        return f"FuncDecl({self.name}, {self.params}, {self.body})"

class ReturnStmt(Node):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class IfStmt(Node):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class Block(Node):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"ExprStmt({self.expr})"

# Expressions
class Identifier(Node):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Id({self.name})"

class Literal(Node):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if isinstance(self.value, str):
            return f'Lit("{self.value}")'
        else:
            return f"Lit({self.value})"

class Unary(Node):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"Unary({self.operator}, {self.right})"

class Binary(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"Binary({self.left}, {self.operator}, {self.right})"

class Assign(Node):
    def __init__(self, left, value):
        self.left = left
        self.value = value
    def __repr__(self):
        return f"Assign({self.left}, {self.value})"

class Call(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
    def __repr__(self):
        return f"Call({self.callee}, {self.args})"

class Index(Node):
    def __init__(self, collection, index):
        self.collection = collection
        self.index = index
    def __repr__(self):
        return f"Index({self.collection}, {self.index})"

# -----------------------
# Parser
# -----------------------
class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.cur = None
        self.peek = None
        self.errors = []
        # **CORREÇÃO 1: Inicializa os tokens para começar a análise**
        self._next_token() # Inicializa self.peek
        self._next_token() # Inicializa self.cur a partir do self.peek, e atualiza self.peek
        
    # ------ token helpers ------
    def _next_token(self):
        """Move forward: cur <- peek ; peek <- lexer.next_token()"""
        self.cur = self.peek
        self.peek = self.lexer.next_token()

    def _cur_is(self, ttype: TokenType):
        return self.cur is not None and self.cur.type == ttype

    def _peek_is(self, ttype: TokenType):
        return self.peek is not None and self.peek.type == ttype

    def expect_peek(self, ttype: TokenType):
        """Se peek for do tipo esperado, consome (move para cur); caso contrário registra erro."""
        if self._peek_is(ttype):
            self._next_token()
            return True
        else:
            self._peek_error(ttype)
            return False

    def _peek_error(self, ttype: TokenType):
        actual = self.peek.type.name if self.peek and self.peek.type != TokenType.EOF else "EOF"
        msg = f"Erro sintático: esperado {ttype.name}, encontrado {actual} (em {self.peek.literal if self.peek else 'fim de arquivo'})"
        self.errors.append(msg)
    
    # ------ entry point ------
    def parse_program(self) -> Program:
        program = Program()
        # enquanto cur não for EOF
        while self.cur and self.cur.type != TokenType.EOF: 
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            # **CORREÇÃO 2: Avançar para o próximo token de statement**
            # (Se parse_statement() não consumiu o token de próxima instrução, 
            # o loop deve avançar. Se o statement foi bem-sucedido, ele deve ter deixado
            # o `cur` no final do statement ou em ';'. O loop principal avança para o próximo statement.)
            if self.cur and self.cur.type != TokenType.EOF:
                 self._next_token() # Avança para o início do próximo statement
            
        return program

    # ------ statements ------
    def parse_statement(self):
        # cur já está no token de início do statement (e foi avançado pelo loop em parse_program)
        if self._cur_is(TokenType.VAR) or self._cur_is(TokenType.CONST):
            kind = self.cur.literal
            return self._parse_var_decl(kind)
        if self._cur_is(TokenType.FUNCTION):
            return self._parse_func_decl()
        if self._cur_is(TokenType.RETURN):
            return self._parse_return()
        if self._cur_is(TokenType.IF):
            return self._parse_if()
        if self._cur_is(TokenType.LBRACE):
            # O bloco precisa ser tratado como statement, mas o _parse_block já consome
            # o { em cur (que já deveria ter sido consumido antes de chamar parse_statement,
            # como no _parse_if) - ajustamos o _parse_block
            return self._parse_block()
        # default: expressão seguida opcionalmente por ';'
        return self._parse_expr_stmt()

    def _parse_var_decl(self, kind='var'):
        # cur == VAR | CONST
        # Espera e consome IDENT (cur <- IDENT)
        if not self.expect_peek(TokenType.IDENT):
            self._synchronize()
            return None
        name = Identifier(self.cur.literal)
        initializer = None
        
        # O Peek é o token após o IDENT
        if self._peek_is(TokenType.ASSIGN):
            self._next_token()  # consume '=' into cur
            self._next_token()  # advance to first token of expression (cur <- expr_token)
            initializer = self.parse_expression() # parse_expression deixa o cur na expressão, o peek no próximo
        
        # Optional semicolon. O token SEMICOLON (ou o próximo) está em peek
        if self._peek_is(TokenType.SEMICOLON):
            self._next_token() # consume ';' into cur
            # O loop principal (parse_program) ou o statement pai chamará _next_token()
            # para avançar para o próximo statement, deixando o peek no próximo token
        
        return VarDecl(kind, name, initializer)

    def _parse_func_decl(self):
        # cur == FUNCTION
        if not self.expect_peek(TokenType.IDENT): # cur <- IDENT
            self._synchronize()
            return None
        name = Identifier(self.cur.literal)
        
        # params: expect '('
        if not self.expect_peek(TokenType.LPAREN): # cur <- LPAREN
            self._synchronize()
            return None
        
        params = []
        # Se peek não é ')' (temos params)
        if not self._peek_is(TokenType.RPAREN):
            while True:
                if not self.expect_peek(TokenType.IDENT): # cur <- IDENT
                    self._synchronize()
                    return None
                params.append(Identifier(self.cur.literal))
                
                if not self._peek_is(TokenType.COMMA):
                    break # Fim dos parâmetros
                
                self._next_token()  # consume ',' into cur
        
        # expect ')'
        if not self.expect_peek(TokenType.RPAREN): # cur <- RPAREN
            self._synchronize()
            return None
            
        # optional arrow return type (we'll accept but ignore type here)
        if self._peek_is(TokenType.ARROW):
            self._next_token() # cur <- ARROW
            if not self.expect_peek(TokenType.IDENT): # cur <- IDENT do tipo
                self._synchronize()
                return None
                
        # body: expect '{'
        if not self.expect_peek(TokenType.LBRACE): # cur <- LBRACE
            self._synchronize()
            return None
            
        # parse body statements until RBRACE (cur já está no LBRACE)
        body = self._parse_block_body()
        
        return FuncDecl(name, params, body)

    def _parse_return(self):
        # cur == RETURN
        value = None
        # Se peek não é ';' ou '}', há uma expressão de retorno
        if not self._peek_is(TokenType.SEMICOLON) and not self._peek_is(TokenType.RBRACE):
            self._next_token() # advance to first token of expression (cur <- expr_token)
            value = self.parse_expression() # parse_expression deixa cur na expressão, peek no próximo
        
        # optional semicolon
        if self._peek_is(TokenType.SEMICOLON):
            self._next_token() # consume ';' into cur
            
        return ReturnStmt(value)

    def _parse_if(self):
        # cur == IF
        if not self.expect_peek(TokenType.LPAREN): # cur <- LPAREN
            self._synchronize()
            return None
            
        self._next_token() # advance to first token of condition (cur <- cond_token)
        cond = self.parse_expression()
        
        if not self.expect_peek(TokenType.RPAREN): # cur <- RPAREN
            self._synchronize()
            return None
            
        # then branch: O token de início da branch está em peek.
        # **CORREÇÃO 4:** Avança para o início do 'then_branch'.
        self._next_token() # cur <- token do then_branch
        then_branch = self.parse_statement()
        
        else_branch = None
        # O token após o then_branch (ou ;) está em peek.
        if self._peek_is(TokenType.ELSE):
            self._next_token() # cur <- ELSE
            self._next_token() # cur <- token do else_branch
            else_branch = self.parse_statement()
            
        return IfStmt(cond, then_branch, else_branch)

    def _parse_block(self):
        # cur == LBRACE
        # Consome '{' e chama o corpo
        # **CORREÇÃO 4:** Se o caller (como parse_statement) deixou o '{' em cur, chamamos o body.
        return self._parse_block_body()

    def _parse_block_body(self):
        # cur já está no LBRACE (consumido pelo caller)
        stmts = []
        while not self._peek_is(TokenType.RBRACE) and not self._peek_is(TokenType.EOF):
            self._next_token() # cur <- token de início do statement
            s = self.parse_statement()
            if s:
                stmts.append(s)
        
        if self._peek_is(TokenType.RBRACE):
            self._next_token() # consume '}' into cur
        else:
             self.errors.append("Erro sintático: esperado } no final do bloco")
             # Não sincroniza aqui, deixa o controle para o caller (se for o caso)
        
        return Block(stmts)

    def _parse_expr_stmt(self):
        # cur já está no token de início da expressão
        expr = self.parse_expression()
        
        # optional semicolon (peek está no token após o final da expressão)
        if self._peek_is(TokenType.SEMICOLON):
            self._next_token() # consume ';' into cur
            
        return ExprStmt(expr)

    # ------ expressions (precedence climbing) ------
    PRECD_UNARY = 8 # Precedência para operadores unários (BANG, MINUS)
    PRECD_CALL_INDEX = 9 # Precedência para operadores postfix (Call, Index)

    PRECEDENCES = {
        TokenType.ASSIGN: 1,# = (right-associative)
        TokenType.OR: 2, # ||
        TokenType.AND: 3, # &&
        TokenType.EQ: 4, TokenType.NOT_EQ: 4, TokenType.STRICT_EQ: 4, TokenType.STRICT_NOT_EQ: 4,
        TokenType.LT: 5, TokenType.GT: 5, TokenType.LTE: 5, TokenType.GTE: 5,
        TokenType.PLUS: 6, TokenType.MINUS: 6,
        TokenType.ASTERISK: 7, TokenType.SLASH: 7,
        # **CORREÇÃO 5:** Adicionando precedências para Unary, Call e Index na tabela, e usando no loop
        TokenType.BANG: PRECD_UNARY, TokenType.MINUS: PRECD_UNARY,
        TokenType.LPAREN: PRECD_CALL_INDEX, # call
        TokenType.LBRACKET: PRECD_CALL_INDEX # index access
    }

    def parse_expression(self, precedence=0):
            left = None
            
            # --- 1. PREFIX PARSING ---
            # Note: Não avançamos o token ao final dessas atribuições (exceto nas recursões internas)
            # O objetivo é terminar esta etapa com cur = "fim do termo esquerdo" e peek = "operador"
            
            if self._cur_is(TokenType.IDENT):
                left = Identifier(self.cur.literal)
            elif self._cur_is(TokenType.NUMBER):
                try:
                    val = float(self.cur.literal)
                except ValueError:
                    val = self.cur.literal
                left = Literal(val)
            elif self._cur_is(TokenType.STRING):
                left = Literal(self.cur.literal)
            elif self._cur_is(TokenType.TRUE):
                left = Literal(True)
            elif self._cur_is(TokenType.FALSE):
                left = Literal(False)
            elif self._cur_is(TokenType.BANG) or self._cur_is(TokenType.MINUS):
                op = self.cur.literal
                self._next_token()
                right = self.parse_expression(self._precedence_of(op))
                left = Unary(op, right)
                # REMOVIDO: return left (deve cair no loop para permitir !a && b)
                
            elif self._cur_is(TokenType.LPAREN):
                self._next_token()
                left = self.parse_expression()
                if not self.expect_peek(TokenType.RPAREN):
                    self._synchronize()
                    return left
                # REMOVIDO: return left (deve cair no loop para permitir (a) + b)
                
            else:
                self.errors.append(f"Erro sintático: token prefixo inesperado {self.cur.type.name}")
                return None

            # --- REMOVIDO O BLOCO "CORREÇÃO 3" AQUI ---
            # Se cur é IDENT, peek já é o operador (+). Não avance!
            
            # --- 2. INFIX / POSTFIX LOOP ---
            while self.peek and not self._peek_is(TokenType.SEMICOLON) and precedence < self._peek_precedence():
                
                if self._peek_is(TokenType.LPAREN):
                    self._next_token()
                    left = self._parse_call(left)
                elif self._peek_is(TokenType.LBRACKET):
                    self._next_token()
                    left = self._parse_index(left)
                else:
                    # Binário: cur é o termo esquerdo, peek é o operador.
                    # Avançamos para cur virar o operador.
                    self._next_token() 
                    left = self._parse_infix(left)
            
            return left
    def _parse_call(self, callee):
        # cur == LPAREN
        args = []
        
        # Se peek é ')' (chamada sem argumentos)
        if self._peek_is(TokenType.RPAREN):
            self._next_token() # consume ')' into cur
            return Call(callee, args)
        
        # parse first arg:
        self._next_token() # cur <- primeiro token do argumento
        args.append(self.parse_expression())
        
        while self._peek_is(TokenType.COMMA):
            self._next_token() # cur <- COMMA
            self._next_token() # cur <- próximo token do argumento
            args.append(self.parse_expression())
            
        # O parse_expression deixa o final do último argumento em cur, e ')' em peek.
        if not self.expect_peek(TokenType.RPAREN): # cur <- RPAREN
            self._synchronize()
            return Call(callee, args) # Retorna o call incompleto
            
        return Call(callee, args)

    def _parse_index(self, collection):
        # cur == LBRACKET
        self._next_token() # advance to index expression (cur <- token da expressão de índice)
        idx = self.parse_expression()
        
        # O parse_expression deixa o final da expressão de índice em cur, e ']' em peek.
        if not self.expect_peek(TokenType.RBRACKET): # cur <- RBRACKET
            self._synchronize()
            return Index(collection, idx)
            
        return Index(collection, idx)

    def _parse_infix(self, left):
        # cur is the operator
        op = self.cur.literal
        op_type = self.cur.type
        cur_prec = self._cur_precedence()
        
        # For right-associative operators (assignment) parse rhs with one less precedence to allow right-assoc
        if op_type == TokenType.ASSIGN:
            # move to expression start on rhs
            self._next_token() # cur <- token de início da expressão (rhs)
            right = self.parse_expression(cur_prec) # **CORREÇÃO 5:** Precedência de Assign é 1, então `cur_prec - 1` seria 0 (minha precedência é 1). Usamos a precedência normal, mas em `parse_expression` garantimos que a recursão com a mesma precedência pare. A regra é: `right = self.parse_expression(cur_prec)` se for left-associative, e `right = self.parse_expression(cur_prec - 1)` se for right-associative.
            
            # left must be assignable (identifier or index)
            if isinstance(left, Identifier) or isinstance(left, Index):
                return Assign(left, right)
            else:
                self.errors.append(f"Erro semântico-sintático: lado esquerdo de atribuição não é atribuível: {left.__class__.__name__}")
                return None
        else:
            # normal left-associative:
            self._next_token() # cur <- token de início da expressão (rhs)
            right = self.parse_expression(cur_prec)
            return Binary(left, op, right)

    def _precedence_of(self, ttype):
        # Se for literal de operador, busca pelo token correspondente no dict de precedências
        if isinstance(ttype, str):
            for tok_type, prec in self.PRECEDENCES.items():
                if tok_type.value == ttype:
                    return prec
        return self.PRECEDENCES.get(ttype, 0)

    def _cur_precedence(self):
        return self._precedence_of(self.cur.type) if self.cur else 0

    def _peek_precedence(self):
        return self._precedence_of(self.peek.type) if self.peek else 0

    # ------ error recovery ------
    def _synchronize(self):
        """Skip tokens until a statement boundary to continue parsing after an error."""
        sync_tokens = {TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF}
        while self.cur and self.cur.type not in sync_tokens:
             if self._peek_is(TokenType.VAR) or self._peek_is(TokenType.CONST) or \
                self._peek_is(TokenType.FUNCTION) or self._peek_is(TokenType.IF):
                # Não consome o próximo token que parece ser o início de um novo statement
                break 
             self._next_token()
        
        # Consome o SEMICOLON/RBRACE para sair do estado de erro e tentar o próximo statement
        if self.cur and self.cur.type in sync_tokens:
            self._next_token()