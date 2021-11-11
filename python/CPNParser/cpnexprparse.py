import ply.yacc as yacc
import cpnexprlex

# List of token names.   This is always required
tokens = cpnexprlex.tokens

# Parsing rules
# precedence = (
#     ('nonassoc', 'LESS', 'GREATER'),  # Nonassociative operators
#     ('nonassoc', 'LEQ', 'GEQ'),
#     ('nonassoc', 'EQUALS', 'NEQ'),
#     ('nonassoc', 'COMA'),
#     ('right', 'IF'),
#     ('right', 'THEN', 'ELSE'),
#     ('left', 'ORELSE', 'ANDALSO'),
#     ('left', 'PLUS', 'MINUS'),
#     ('left', 'TIMES', 'DIVIDE'),
#     ('right', 'UMINUS'),
#     ('right', 'NOT'),
# )

precedence = (
    ('right', 'IF'),
    ('right', 'THEN', 'ELSE'),
    ('left', 'ORELSE', 'ANDALSO'),
    ('left', 'LESS', 'LEQ', 'EQUALS', 'NEQ', 'GREATER', 'GEQ'),  # Nonassociative operators
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
def p_statement_if(t):
    '''expression : IF expression THEN statement %prec IF
                 | IF expression THEN statement ELSE statement'''

    t[0] = "ITE({0}, {1}".format(t[2], t[4])
    # ELSE
    if t[6] is not None:
        t[0] = t[0] + ", {0})".format(t[6])
    else:
        t[0] = t[0] + ", empty)"

# func call
def p_statement_func(t):
    '''expression : NAME LPAREN expression RPAREN'''

    t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])


def p_expression_group(t):
    '''expression : LPAREN expression RPAREN
                | LBRACK expression RBRACK'''
    t[0] = str(t[2])


def p_expression_list(t):
    '''expression : expression COMA item
                  | expression item
                  | item'''
    t[0] = "{0}".format(t[1])
    if len(t) == 4:
        t[0] = t[0] + " , {0}".format(t[3])
    elif len(t) == 3:
        t[0] = t[0] + " {0}".format(t[2])


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
    else:
        t[0] = "{0}".format(t[1])


# expression
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''

    op = "{0} {1} {2}".format(t[1], t[2], t[3])
    identifier = ap_identifier(op)
    t[0] = "AP(\"{0}\", {1})".format(identifier, op)


def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    # t[0] = "{0}".format(-t[2])
    t[0] = str(-t[2])


def p_expression_not(t):
    'expression : NOT expression'
    # t[0] = t[2]
    t[0] = "NOT({0})".format(t[2])


def p_expression_number(t):
    'item : NUMBER'
    t[0] = t[1]


def p_expression_bool(t):
    'item : BOOL'
    t[0] = str(t[1])


def p_expression_string(t):
    'item : STRING'
    t[0] = str(t[1])


def p_expression_name(t):
    'item : NAME'
    t[0] = str(t[1])


def p_error(t):
    print("Syntax error at '%s'" % t.value)


# Build the parser
cpnparser = yacc.yacc(debug=False, write_tables=False)


def parse(data, debug=0):
    cpnparser.error = 0
    p = cpnparser.parse(data, debug=debug)
    if cpnparser.error:
        return None
    return p