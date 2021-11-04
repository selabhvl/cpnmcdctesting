import ply.lex as lex
import ply.yacc as yacc

# List of reserved names.
reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'orelse': 'ORELSE',
    'andalso': 'ANDALSO',
    'not': 'NOT'
}

# List of token names.   This is always required
tokens = [
    'NAME', 'ASSIGN', 'NUMBER', 'BOOL',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQUALS', 'NEQ', 'LEQ', 'LESS', 'GEQ', 'GREATER',
    'LPAREN', 'RPAREN', 'COMA'
] + list(reserved.values())

# Tokens
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
t_COMA = r'\,'
# t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'


# A regular expression rule with some action code
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
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


# Ignored characters
t_ignore = " \t"
t_ignore_COMMENT = r"\(\*.*\*\)"          # Ignores the comments (* blabla *)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Parsing rules
precedence = (
    ('nonassoc', 'LESS', 'GREATER'),  # Nonassociative operators
    ('nonassoc', 'LEQ', 'GEQ'),
    ('nonassoc', 'EQUALS', 'NEQ'),
    ('nonassoc', 'COMA'),
    ('right', 'IF'),
    ('left', 'THEN', 'ELSE'),
    ('left', 'ORELSE', 'ANDALSO'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
    ('right', 'NOT'),
)

# dictionary of names
names = {}

# dictionary of expressions
ex = {}

# dictionary of atomic propositions
ap = {}


def ap_identifier(op):
    # type: (str) -> str
    if op not in ap:
        ap[op] = len(ap) + 1
    identifier = ap[op]
    return identifier


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    names[t[1]] = t[3]


def p_statement_expr(t):
    'statement : expression'
    if t[1] not in ex:
        ex[t[1]] = "id{0}".format(len(ex) + 1)
    identifier = ex[t[1]]

    t[0] = "EXPR(\"{0}\", {1})".format(identifier, t[1])


# if statement
def p_statement_if(p):
    '''statement : IF expression THEN statement %prec IF
                 | IF expression THEN statement ELSE statement'''
    if p[3]:
        p[0] = p[5]
    else:
        if p[7] is not None:
            p[0] = p[7]


# comparison
def p_comparison_binop(t):
    '''expression : expression EQUALS expression
                  | expression NEQ expression
                  | expression LESS expression
                  | expression LEQ expression
                  | expression GREATER expression
                  | expression GEQ expression
                  | expression ORELSE expression
                  | expression ANDALSO expression'''

    if t[2] in {'=', '<>', '<', '<=', '>', '>='}:
        op = "{0} {1} {2}".format(t[1], t[2], t[3])
        identifier = ap_identifier(op)
        t[0] = "AP(\"{0}\", {1})".format(identifier, op)
    elif t[2] == 'orelse':
        t[0] = "OR({0}, {1})".format(t[1], t[3])
    elif t[2] == 'andalso':
        t[0] = "AND({0}, {1})".format(t[1], t[3])


def p_expression_list(t):
    '''expression : expression COMA expression'''
    t[0] = "AND({0}, {1})".format(t[1], t[3])


# expression
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
'''

    op = "{0} {1} {2}".format(t[1], t[2], t[3])
    identifier = ap_identifier(op)
    t[0] = "AP(\"{0}\", {1})".format(identifier, op)


def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = str(t[2])


def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    # t[0] = "{0}".format(-t[2])
    t[0] = str(-t[2])


def p_expression_not(t):
    'expression : NOT expression'
    # t[0] = t[2]
    t[0] = "NOT({0})".format(t[2])


def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]


def p_expression_bool(t):
    'expression : BOOL'
    t[0] = str(t[1])


def p_expression_name(t):
    'expression : NAME'
    t[0] = str(t[1])

    # if t[1] not in names:
    #     names[t[1]] = len(names)
    # t[0] = names[t[1]]

    # try:
    #     t[0] = names[t[1]]
    # except LookupError:
    #     print("Undefined name '%s'" % t[1])
    #     t[0] = 0


def p_error(t):
    print("Syntax error at '%s'" % t.value)


if __name__ == "__main__":
    # Build the lexer
    lexer = lex.lex()

    # Build the parser
    parser = yacc.yacc()

    # Example:
    # (a < 1) orelse (b > 10) andalso not (c > 20)

    while True:
        try:
            s = input('calc > ')  # Use raw_input on Python 2
        except EOFError:
            break
        res = parser.parse(s)
        print(res)
