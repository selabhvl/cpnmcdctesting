import ply.lex as lex


# List of reserved names.
reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'orelse': 'ORELSE',
    'andalso': 'ANDALSO',
    'fn': 'FN',
    'let': 'LET',
    'fun': 'FUN',
    'val': 'VAL',
    'in': 'IN',
    'end': 'END',
}

# List of token names.   This is always required
tokens = [
    'NAME', 'ASSIGN', 'STRING', 'NUMBER', 'BOOL',
    'APP', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'CONS',
    'EQUALS', 'NEQ', 'LEQ', 'LESS', 'GEQ', 'GREATER',
    'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'COMA', 'SEMI', 'DOT', 'TICK', 'TILDE', 'TO', 'CHAR',
    'HAT', 'SHAT', 'REF', 'PIPE', 'LCURL', 'RCURL', 'COLON',
] + list(reserved.values())

# Tokens
t_APP = r'\+\+'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r':='
t_EQUALS = r'='
t_NEQ = r'<>'
t_LEQ = r'<='
t_LESS = r'<'
t_GEQ = r'>='
t_GREATER = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_COMA = r'\,'
t_SEMI = r';'
t_DOT = r'\.'
t_STRING = r'(\"|\').*?(\"|\')'
t_CONS = r'::'
t_TICK = r'\`'
t_TILDE = r'~'
t_TO = r'=>'
t_CHAR = r'\#'
t_HAT = r'\^\^'
t_SHAT = r'\^'
t_REF = r'!'
t_PIPE = r'\|'
t_LCURL = r'{'
t_RCURL = r'}'
t_COLON = ':'

# t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'


# Ignored characters
t_ignore = " \t\n"
t_ignore_COMMENT = r"\(\*.*\*\)"          # Ignores the comments (* blabla *)

# A regular expression rule with some action code
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9\'\.]*'
    t.type = reserved.get(t.value, 'NAME')  # Check for reserved words
    return t


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_BOOL(t):
    r'true|false'
    try:
        t.value = bool(t.value)
    except ValueError:
        print("Not properly formatted Bool value %d", t.value)
        t.value = False
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lex.lex()
