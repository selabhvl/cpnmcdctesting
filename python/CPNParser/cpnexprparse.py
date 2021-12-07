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
#     ('right', 'NOT'),
# )

precedence = (
    ('right', 'NAME'),
    ('right', 'IF'),
    ('right', 'THEN', 'ELSE'),
    ('left', 'ORELSE', 'ANDALSO'),
    ('left', 'LESS', 'LEQ', 'EQUALS', 'NEQ', 'GREATER', 'GEQ'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'TILDE'),
    ('right', 'NOT'),
    ('right', 'CONS'),
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

def ex_identifier(op):
    # type: (str) -> str
    if op not in ex:
        ex[op] = "id{0}".format(len(ex) + 1)
    identifier = ex[op]
    return identifier


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    names[t[1]] = t[3]

# annotations = arithmetic expression (arcs)
def p_statement_expr(t):
    'statement : expression'
    t[0] = t[1]

# condition = bool expression (transitions)
def p_statement_guard(t):
    'statement : guard'
    identifier = ex_identifier(t[1])
    t[0] = "EXPR(\"{0}\", {1})".format(identifier, t[1])

# if statement
def p_statement_expression_if(t):
    '''expression : IF condition THEN statement %prec IF
                 | IF condition THEN statement ELSE statement'''

    identifier = ex_identifier(t[2])
    t[0] = "if EXPR(\"{0}\", {1}) then {2}".format(identifier, t[2], t[4])
    # ELSE
    if t[6] is not None:
        t[0] = t[0] + " else {0}".format(t[6])

def p_statement_condition_if(t):
    '''condition : IF condition THEN statement %prec IF
                 | IF condition THEN statement ELSE statement'''

    t[0] = "ITE({0}, {1}".format(t[2], t[4])
    # ELSE
    if t[6] is not None:
        t[0] = t[0] + ", {0})".format(t[6])
    else:
        t[0] = t[0] + ", empty)"


# func call
def p_expression_func(t):
    '''expression : expression LPAREN expression_list RPAREN
                    | expression expression'''

    if len(t) == 5:
        t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])
    else:
        t[0] = "{0} {1}".format(t[1], t[2])

def p_expression_list(t):
    '''expression_list : expression_list COMA expression
                  | expression'''

    if len(t) == 4:
        t[0] = "{0}, {1}".format(t[1], t[3])
    elif len(t) == 2:
        t[0] = "{0}".format(t[1])
    else:
        assert False

def p_condition_group(t):
    '''guard : LBRACK condition_list RBRACK
              | condition'''
    if len(t) == 4:
        t[0] = "[{0}]".format(t[2])
    elif len(t) == 2:
        t[0] = "{0}".format(t[1])
    else:
        assert False

def p_expression_nil(t):
    '''expression : LBRACK RBRACK'''
    t[0] = "[]"


def p_expression_fn(t):
    '''expression : FN NAME TO expression'''
    t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])

def p_expression_group(t):
    '''expression : LPAREN expression RPAREN'''
    t[0] = "({0})".format(t[2])

def p_expression_tuple(t):
    '''expression : LPAREN expression_list RPAREN'''
    t[0] = "({0})".format(t[2])

def p_expression_unit(t):
    '''expression : LPAREN RPAREN'''
    t[0] = "()"

def p_condition_list(t):
    '''condition_list : condition_list COMA condition
                        | condition'''

    if len(t) == 4:
        t[0] = "AND({0}, {1})".format(t[1], t[3])
    elif len(t) == 2:
        t[0] = "{0}".format(t[1])
    else:
        assert False


# Bool comparison
def p_condition_not(t):
    'condition : NOT condition'
    # t[0] = t[2]
    t[0] = "NOT({0})".format(t[2])

def p_condition_paren(t):
    'condition : LPAREN condition RPAREN'
    # t[0] = t[2]
    t[0] = "({0})".format(t[2])


def p_condition_expr(t):
    'condition : expression'
    # t[0] = t[2]
    t[0] = "{0}".format(t[1])

def p_comparison_binop(t):
    '''condition : expression EQUALS expression
                  | expression NEQ expression
                  | expression LESS expression
                  | expression LEQ expression
                  | expression GREATER expression
                  | expression GEQ expression
                  | condition ORELSE condition
                  | condition ANDALSO condition'''

    if t[2] in {'=', '<>', '<', '<=', '>', '>='}:
        print("Volker")
        op = "{0} {1} {2}".format(t[1], t[2], t[3])
        identifier = ap_identifier(op)
        t[0] = "AP(\"{0}\", {1})".format(identifier, op)
    elif t[2] == 'orelse':
        t[0] = "OR({0}, {1})".format(t[1], t[3])
    elif t[2] == 'andalso':
        t[0] = "AND({0}, {1})".format(t[1], t[3])
    else:
        assert False
        t[0] = "{0}".format(t[1])


# expression
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression CONS expression
                  | expression TICK expression'''

    op = "{0} {1} {2}".format(t[1], t[2], t[3])
    # identifier = ap_identifier(op)
    # t[0] = "(\"{0}\", {1})".format(identifier, op)
    t[0] = "{0}".format(op)


def p_expression_tilde(t):
    'expression : TILDE expression'
    # t[0] = "{0}".format(-t[2])
    t[0] = "{0} {1}".format(t[1], t[2])

def p_condition_item(t):
    'condition : item'
    t[0] = t[1]

def p_expression_item(t):
    'expression : item'
    t[0] = t[1]

def p_item_number(t):
    'item : NUMBER'
    t[0] = str(t[1])


def p_item_bool(t):
    'item : BOOL'
    t[0] = str(t[1])


def p_item_string(t):
    'item : STRING'
    t[0] = str(t[1])


def p_item_name(t):
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
        # return None
        return data
    return p