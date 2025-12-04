from enum import Enum

class TokenType(Enum):
    # End of File
    EOF = "EOF"

    # Palavras-chave
    FUNCTION = "FUNCTION"
    VAR = "VAR"
    CONST = "CONST"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    RETURN = "RETURN"
    TRUE = "TRUE"
    FALSE = "FALSE"
    VOID = "VOID"
    NULL = "NULL"

    # Identificadores e Literais
    IDENT = "IDENT"  # Nomes de variáveis/funções
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Operadores
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    ASTERISK = "*"
    SLASH = "/"
    MODULO = "%"
    BANG = "!"
    
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    
    EQ = "=="
    NOT_EQ = "!="
    STRICT_EQ = "==="
    STRICT_NOT_EQ = "!=="

    AND = "&&"
    OR = "||"

    # Delimitadores
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    DOT = "."
    COLON = ":"
    ARROW = "->"
    SEMICOLON = ";"

    # Desconhecido
    UNKNOWN = "UNKNOWN"

class Token:
    def __init__(self, type: TokenType, literal: str):
        self.type = type
        self.literal = literal

    def __repr__(self):
        return f"Token({self.type.name}, '{self.literal}')"

# Mapeamento de palavras-chave para seus Tipos de Token
keywords = {
    "function": TokenType.FUNCTION,
    "var": TokenType.VAR,
    "let": TokenType.VAR,  # 'let' será tratado como VAR
    "const": TokenType.CONST,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "void": TokenType.VOID,
    "null": TokenType.NULL,
}

def lookup_ident(ident: str) -> TokenType:
    """Verifica se um identificador é uma palavra-chave."""
    return keywords.get(ident, TokenType.IDENT)
