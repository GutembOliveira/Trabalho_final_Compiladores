from tokens import Token, TokenType, lookup_ident

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0  # Posição atual no código
        self.read_position = 0  # Próxima posição a ser lida
        self.ch = ''  # Caractere atual
        self._read_char()

    def _read_char(self):
        """Lê o próximo caractere do código-fonte."""
        if self.read_position >= len(self.source):
            self.ch = ''  # EOF
        else:
            self.ch = self.source[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def _peek_char(self) -> str:
        """Olha o próximo caractere sem avançar no código."""
        if self.read_position >= len(self.source):
            return ''
        return self.source[self.read_position]

    def _skip_whitespace(self):
        """Pula espaços em branco, tabulações e novas linhas."""
        while self.ch in [' ', '\t', '\n', '\r']:
            self._read_char()

    def _skip_comment(self):
        """Pula todos os caracteres até o final da linha (//)."""
        # Enquanto não for nova linha E não for fim do arquivo
        while self.ch != '\n' and self.ch != '':
            self._read_char()
        # O self.ch agora é '\n' (ou ''). O _read_char() em next_token irá pular isso.

    def next_token(self) -> Token:
        """Retorna o próximo token do código-fonte."""
        self._skip_whitespace()

        token = None

        # Lógica para identificar o token baseado no caractere atual
        if self.ch == '=':
            if self._peek_char() == '=':
                self._read_char()
                if self._peek_char() == '=':
                    self._read_char()
                    token = Token(TokenType.STRICT_EQ, '===')
                else:
                    token = Token(TokenType.EQ, '==')
            else:
                token = Token(TokenType.ASSIGN, '=')
        elif self.ch == '!':
            if self._peek_char() == '=':
                self._read_char()
                if self._peek_char() == '=':
                    self._read_char()
                    token = Token(TokenType.STRICT_NOT_EQ, '!==')
                else:
                    token = Token(TokenType.NOT_EQ, '!=')
            else:
                token = Token(TokenType.BANG, '!')
        elif self.ch == '+':
            token = Token(TokenType.PLUS, '+')
        elif self.ch == '-':
            if self._peek_char() == '>':
                self._read_char()
                token = Token(TokenType.ARROW, '->')
            else:
                token = Token(TokenType.MINUS, '-')
        elif self.ch == '*':
            token = Token(TokenType.ASTERISK, '*')
        elif self.ch == '/':
            if self._peek_char() == '/':  # Verifica se é //
                self._read_char()         # Consome o primeiro '/'
                self._read_char()         # Consome o segundo '/'
                self._skip_comment()      # Pula o restante da linha
                return self.next_token()  # Reinicia o ciclo para buscar o próximo token VÁLIDO
            else:
                token = Token(TokenType.SLASH, '/')

        elif self.ch == '<':
            if self._peek_char() == '=':
                self._read_char()
                token = Token(TokenType.LTE, '<=')
            else:
                token = Token(TokenType.LT, '<')
        elif self.ch == '>':
            if self._peek_char() == '=':
                self._read_char()
                token = Token(TokenType.GTE, '>=')
            else:
                token = Token(TokenType.GT, '>')
        elif self.ch == '&':
            if self._peek_char() == '&':
                self._read_char()
                token = Token(TokenType.AND, '&&')
        elif self.ch == '|':
            if self._peek_char() == '|':
                self._read_char()
                token = Token(TokenType.OR, '||')
        elif self.ch == '(':
            token = Token(TokenType.LPAREN, '(')
        elif self.ch == ')':
            token = Token(TokenType.RPAREN, ')')
        elif self.ch == '{':
            token = Token(TokenType.LBRACE, '{')
        elif self.ch == '}':
            token = Token(TokenType.RBRACE, '}')
        elif self.ch == '[':
            token = Token(TokenType.LBRACKET, '[')
        elif self.ch == ']':
            token = Token(TokenType.RBRACKET, ']')
        elif self.ch == ',':
            token = Token(TokenType.COMMA, ',')
        elif self.ch == ':':
            token = Token(TokenType.COLON, ':')
        elif self.ch == ';':
            token = Token(TokenType.SEMICOLON, ';')
        elif self.ch == '.':
            token = Token(TokenType.DOT, '.')
        elif self.ch == '"':
            literal = self._read_string()
            token = Token(TokenType.STRING, literal)
            #self._read_char()
        elif self.ch == '':
            token = Token(TokenType.EOF, '')
        else:
            if self._is_letter(self.ch):
                literal = self._read_identifier()
                tok_type = lookup_ident(literal)
                return Token(tok_type, literal)
            elif self._is_digit(self.ch):
                literal = self._read_number()
                return Token(TokenType.NUMBER, literal)
            else:
                token = Token(TokenType.UNKNOWN, self.ch)

        self._read_char()
        return token

    def _is_letter(self, char: str) -> bool:
        """Verifica se um caractere é uma letra ou sublinhado."""
        return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char == '_'

    def _is_digit(self, char: str) -> bool:
        """Verifica se um caractere é um dígito."""
        return '0' <= char <= '9'

    def _read_identifier(self) -> str:
        """Lê um identificador completo."""
        start_pos = self.position
        while self._is_letter(self.ch) or self._is_digit(self.ch):
            self._read_char()
        return self.source[start_pos:self.position]

    def _read_number(self) -> str:
        """Lê um número (int ou float)."""
        start_pos = self.position
        while self._is_digit(self.ch):
            self._read_char()
        if self.ch == '.':
            self._read_char()
            while self._is_digit(self.ch):
                self._read_char()
        return self.source[start_pos:self.position]

    def _read_string(self) -> str:
        """Lê uma string entre aspas."""
        self._read_char() # Pula a aspa inicial
        start_pos = self.position
        while self.ch != '"' and self.ch != '':
            self._read_char()
        literal = self.source[start_pos:self.position]
        
        return literal