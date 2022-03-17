import ply.yacc as yacc
import cpnexprlex
import tempfile
from enum import Enum

# List of token names.   This is always required
tokens = cpnexprlex.tokens
start = 'statement'

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
    ('right', 'IF', 'THEN', 'ELSE'),  # VS not sure if ELSE should be strongest?
    ('left', 'ORELSE', 'ANDALSO'),
    ('nonassoc', 'LESS', 'LEQ', 'EQUALS', 'NEQ', 'GREATER', 'GEQ'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'TICK'),
    ('right', 'TILDE'),
#    ('right', 'NOT'),
    ('right', 'NOT_2'),
    ('left', 'CONS'),
    ('left', 'FCALL'),  # virtual!
)

# dictionary of names
names = {}

# dictionary of expressions
ex = {}

def ex_identifier(op):
    # type: (str) -> str
    if op not in ex:
        ex[op] = "id{0}".format(len(ex) + 1)
    identifier = ex[op]
    return identifier


class ASTNode(Enum):
    ID = 0
    EXPR = 1
    ITE = 2
    CALL = 3
    LIST = 4
    NIL = 5
    TILDE = 6
    GUARDS = 7
    BINCOND = 8
    BINEXP = 9
    FN = 10
    TUPLE = 11
    NOT = 12  # TODO: only "!"?
    GUARD = 13
    CONSTRUCTOR = 14
    HASH = 15


# class BinOp(Enum):
#     EQUALS = 1
#     NEQ = 2
#     LESS = 3
#     LEQ = 4
#     GREATER = 5
#     GEQ = 6
#     ORELSE = 7
#     ANDALSO = 8
#
#     @staticmethod
#     def from_string(cpn_bin_op):
#         # type: (str) -> str
#         # Receives a binary operation from a non-instrumented CPNTool file
#         # and returns the type of operation. E.g: BinOp.from_string("andalso") --> AND
#         return ""


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    names[t[1]] = t[3]


# condition = bool expression (transitions)
# def p_statement_guard(t):
#     'statement : guard'
#     identifier = ex_identifier(t[1])
#     t[0] = (ASTNode.EXPR, identifier, t[1])


def p_expression_harsh(t):
    '''expression : CHAR NAME expression
                    | CHAR NUMBER expression'''

    # t[0] = "{0}{1} {2}".format(t[1], t[2], t[3])
    t[0] = (ASTNode.HASH, t[2], t[3])


# if statement
def p_statement_expression_if(t):
    '''expression : IF expression THEN expression ELSE expression'''

    # list not hashable (required for "ex" dictionary)
    # identifier = ex_identifier(t[2])
    id_list = id(t[2])
    identifier = ex_identifier(str(id_list))
    if len(t) == 7:
        t[0] = (ASTNode.ITE, identifier, t[2], t[4], t[6])
    else:
        t[0] = (ASTNode.ITE, identifier, t[2], t[4], None)


# func call
def p_expression_func_brackets(t):
    # TODO: untested
    '''expression : LPAREN expression RPAREN expressions %prec FCALL'''
    t[0] = (ASTNode.CALL, t[2], t[4])


def p_expression_func_id_one(t):
    '''expression : NAME expressions %prec FCALL'''
    t[0] = (ASTNode.CALL, (ASTNode.ID, t[1]), t[2])


def p_expression_constructor(t):
    '''expression : NAME LPAREN expression_list RPAREN'''
    t[0] = (ASTNode.CONSTRUCTOR, (ASTNode.ID, t[1]), t[3])


def p_item_or_tuple(t):
    '''iOt : item
           | tuple'''
    t[0] = t[1]

def p_expressions(t):  # never empty.
    '''expressions : expressions iOt
                    | expressions LPAREN expression RPAREN
                    | LPAREN expression RPAREN
                    | iOt'''  # TODO XXX: No longer IDs below!
    # TODO: We loose info about parens, so we can't pretty-print 1:1 later.
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 3:
        t[0] = t[1] + [t[2]]
    elif len(t) == 4:
        t[0] = [t[2]]
    elif len(t) == 5:
        t[0] = t[1] + [t[3]]
    else:
        assert False, t


def p_expression_list(t):
    '''expression_list : expression_list COMA expression
                  | expression'''

    # Using real lists here
    if len(t) == 4:
        # t[0] = "{0}, {1}".format(t[1], t[3])
        t[0] = t[1] + [t[3]]
    elif len(t) == 2:
        # t[0] = "{0}".format(t[1])
        t[0] = [t[1]]
    else:
        assert False


def p_condition_single(t):
    '''guard : expression'''
    id_list = id(t[1])
    identifier = ex_identifier(str(id_list))
    t[0] = (ASTNode.GUARD, identifier, t[1])

def p_condition_group(t):
    '''guard : LBRACK expression_list RBRACK'''
    if len(t) == 4:
        # t[0] = "EXPR(\"{0}\", {1})".format(identifier, t[2])
        # list not hashable (required for "ex" dictionary)
        # identifier = ex_identifier(t[2])
        id_list = id(t[2])
        identifier = ex_identifier(str(id_list))
        t[0] = (ASTNode.GUARDS, identifier, t[2])
    elif len(t) == 2:
        # guard : LBRACK RBRACK
        # TODO: probably wrong.
        assert False
    else:
        assert False


def p_expression_nil(t):
    '''expression : LBRACK RBRACK'''
    t[0] = (ASTNode.NIL, )


def p_expression_list_brack(t):
    '''expression : LBRACK expression_list RBRACK'''
    # t[0] = "{0} {1} {2}".format(t[1], t[2], t[3])
    t[0] = (ASTNode.LIST, t[2])


def p_expression_fn(t):
    '''expression : FN NAME TO expression'''
    # t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])
    t[0] = (ASTNode.FN, t[2], t[4])


def p_expression_unit(t):
    '''item : LPAREN RPAREN'''
    t[0] = (ASTNode.TUPLE, None)


def p_expression_singleton(t):
    '''expression : LPAREN expression RPAREN'''
    t[0] = t[2]  # Losing formatting here.


def p_expression_is_a_tuple(t):
    '''expression : tuple'''
    t[0] = t[1]

def p_expression_tuple(t):
    '''tuple : LPAREN expression_list RPAREN'''
    # t[0] = "({0})".format(t[2])
    # TODO: `(x)` is not a "1-tuple", I think!
    t[0] = (ASTNode.TUPLE, t[2])


# # Bool comparison
# Unclear TODO: incomplete
def p_statement_not(t):
    '''expression : NOT_2 expression'''
    # t[0] = t[2]
    # t[0] = "{0} {1}".format(t[1], t[2])
    t[0] = (ASTNode.NOT, t[1], t[2])
    assert False


def p_comparison_binop(t):
    '''expression : expression EQUALS expression
                  | expression NEQ expression
                  | expression LESS expression
                  | expression LEQ expression
                  | expression GREATER expression
                  | expression GEQ expression
                  | expression ORELSE expression
                  | expression ANDALSO expression'''

    t[0] = (ASTNode.BINCOND, t[1], t[2], t[3])  # infix as before!


# expression
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression CONS expression
                  | expression TICK expression
                  | expression APP expression
                  | expression HAT expression'''

    t[0] = (ASTNode.BINEXP, t[1], t[2], t[3])  # infix as before!


def p_expression_tilde(t):
    'expression : TILDE expression'
    # t[0] = "{0}".format(-t[2])
    # t[0] = "{0} {1}".format(t[1], t[2])
    t[0] = (ASTNode.TILDE, t[1], t[2])


def p_expression_item(t):
    'expression : item'
    t[0] = t[1]


# TODO XXX `ID` should better be called `item`...
def p_item_number(t):
    'item : NUMBER'
    t[0] = ASTNode.ID, str(t[1])


def p_item_bool(t):
    'item : BOOL'
    t[0] = ASTNode.ID, str(t[1])


def p_item_string(t):
    'item : STRING'
    t[0] = ASTNode.ID, str(t[1])


def p_item_name(t):
    'item : NAME'
    t[0] = ASTNode.ID, str(t[1])


def p_error(t):
    # print("Syntax error at '%s'" % t.value)
    print("Syntax error at '{0}', returning {1}".format(t.value, t))
    # t.error = 1
    raise SyntaxError


# Build the parser
tmpdirname = "/temp/"  # tempfile.TemporaryDirectory()
annot_parser = yacc.yacc(start='expression', debug=tmpdirname + 'parser.out', write_tables=False)
cond_parser = yacc.yacc(start='guard', debug=tmpdirname + 'guardparser.out', write_tables=False)

# Arcs in the CPN
def parse_annot(data, debug=0):
    annot_parser.error = 0
    try:
        p = annot_parser.parse(data, debug=debug)
        if annot_parser.error:
            return data
        return p
    except:
        print("Exception: {0}".format(data))
        raise

# Transitions in the CPN
def parse_cond(data, debug=0):
    cond_parser.error = 0
    try:
        p = cond_parser.parse(data, debug=debug)
        if cond_parser.error:
            return data
        return p
    except:
        print("Exception: {0}".format(data))
        raise
