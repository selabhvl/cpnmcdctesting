import ply.yacc as yacc
import cpnexprlex
import tempfile
from enum import Enum

# This grammar is a coarse approximation of https://smlfamily.github.io/sml97-defn.pdf
#   that does the job for our models.
# List of token names.   This is always required
tokens = cpnexprlex.tokens
start = 'fdecls'

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
    ('right', 'REF'),
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
    REF = 12
    GUARD = 13
    CONSTRUCTOR = 14
    HASH = 15
    FUN = 16
    VAL = 17
    ASSIGN = 18
    LET = 19
    TYPED = 20
    FUNDECL = 21
    FNDECL = 22
    CASE = 23
    CASEEXP = 24
    TLGUARD = 25
    HASH_STR = 26

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def p_statement_assign(t):
    'expression : NAME ASSIGN expression'
    t[0] = (ASTNode.ASSIGN, t[1], t[3])


# condition = bool expression (transitions)
# def p_statement_guard(t):
#     'statement : guard'
#     identifier = ex_identifier(t[1])
#     t[0] = (ASTNode.EXPR, identifier, t[1])


def p_expression_hash(t):
    '''expression : CHAR NAME expression
                    | CHAR NUMBER expression'''

    # t[0] = "{0}{1} {2}".format(t[1], t[2], t[3])
    t[0] = (ASTNode.HASH, t[2], t[3])


def p_expression_hash_char(t):
    '''expression : CHAR STRING'''
    # t[0] = "{0}{1} {2}".format(t[1], t[2], t[3])
    t[0] = (ASTNode.HASH_STR, t[2])


# if statement
def p_statement_expression_if(t):
    '''expression : IF expression THEN expression ELSE expression'''

    # list not hashable (required for "ex" dictionary)
    # identifier = ex_identifier(t[2])
    id_list = str(t[2])
    identifier = ex_identifier(id_list)
    if len(t) == 7:
        t[0] = (ASTNode.ITE, identifier, t[2], t[4], t[6])
    else:
        t[0] = (ASTNode.ITE, identifier, t[2], t[4], None)


# func call
# def p_expression_func_brackets(t):
#     # TODO: untested
#     '''expression : LPAREN expression RPAREN expressions %prec FCALL'''
#     t[0] = (ASTNode.CALL, t[2], t[4])


def p_expression_func_id_one(t):
    '''item : item item %prec FCALL'''
    t[0] = (ASTNode.CALL, t[1], t[2])


def p_expression_constructor(t):
    '''item : NAME LPAREN expression_list RPAREN'''
    t[0] = (ASTNode.CONSTRUCTOR, (ASTNode.ID, t[1]), t[3])


def p_item_or_tuple(t):
    '''iOt : item
           | item COLON NAME'''
    # FIXME: we gobble type annotations!
    t[0] = t[1]

def p_expressions(t):  # never empty.
    '''expressions : expressions iOt
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


def mogrify_guard(t):
    # TODO: it seems we need an analysis of incoming edges to get this right.
    #    So disable for now, shouldn't make a difference.
    return t
    assert False  # NOT REACHED, disabled for the moment
    if t[0] == ASTNode.BINCOND and t[2] == "=" and t[1][0] == ASTNode.ID:
        return (ASTNode.TLGUARD, t[1], t[3])
    else:
        return t


def p_condition_single(t):
    '''guard : expression'''
    id_list = str(t[1])
    identifier = ex_identifier(id_list)
    t[0] = (ASTNode.GUARD, identifier, mogrify_guard(t[1]))

def p_condition_group(t):
    '''guard : LBRACK expression_list RBRACK'''
    if len(t) == 4:
        # t[0] = "EXPR(\"{0}\", {1})".format(identifier, t[2])
        # list not hashable (required for "ex" dictionary)
        # identifier = ex_identifier(t[2])
        id_list = str(t[2])
        identifier = ex_identifier(id_list)
        t[0] = (ASTNode.GUARDS, identifier, map(mogrify_guard,t[2]))
    elif len(t) == 2:
        # guard : LBRACK RBRACK
        # TODO: probably wrong.
        assert False
    else:
        assert False


def p_expression_nil(t):
    '''item : LBRACK RBRACK'''
    t[0] = (ASTNode.NIL, )


def p_expression_list_brack(t):
    '''item : LBRACK expression_list RBRACK'''
    # t[0] = "{0} {1} {2}".format(t[1], t[2], t[3])
    t[0] = (ASTNode.LIST, t[2])


def p_expression_fn(t):
    '''expression : FN fnrhs'''
    # t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])
    t[0] = (ASTNode.FNDECL, t[2])


def p_expression_fnrhs(t):
    '''fnrhs : fnrhs PIPE expressions TO expression
                  | expressions TO expression'''
    # t[0] = "{0} {1} {2} {3}".format(t[1], t[2], t[3], t[4])
    if len(t) == 4:
        t[0] = [(ASTNode.FN, t[1], t[3])]
    else:
        assert len(t) == 6
        t[0] = t[1] + [(ASTNode.FN, t[3], t[5])]


def p_fun_decl(t):
    '''fdecl : FUN frhs
             | FUN frhs SEMI'''
    t[0] = (ASTNode.FUNDECL, t[2])

def p_fun_frhs(t):
    '''frhs : frhs PIPE NAME expressions EQUALS expression
            |           NAME expressions EQUALS expression'''
    if len(t) == 5:
        t[0] = [(ASTNode.FUN, t[1], t[2], t[4])]
    else:
        t[0] = t[1] + [(ASTNode.FUN, t[3], t[4], t[6])]


def p_fun_decls(t):
    '''fdecls : fdecls fdecl
              | fdecl'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        assert len(t) == 3
        t[0] = t[1] + [t[2]]


def p_val_decls(t):
    '''fdecl : VAL iOt EQUALS expression
             | VAL iOt EQUALS expression SEMI'''
    # iOt so that we can parse type annos
    t[0] = (ASTNode.VAL, t[2], t[4])


def p_expression_let(t):
    'expression : LET valOrFuns IN expression END'
    t[0] = (ASTNode.LET, t[2], t[4])


def p_valOrFuns(t):
    '''valOrFuns : valOrFuns valOrFun
                 | valOrFun'''
    if len(t) == 2:
        t[0] = [t[1]]
    elif len(t) == 3:
        t[0] = t[1] = [t[2]]
    else:
        assert len(t) == 4
        t[0] = t[1] + [t[3]]


def p_valOrFun_val(t):
    '''valOrFun : VAL iOt EQUALS expression
                | VAL iOt EQUALS expression SEMI'''
    t[0] = (ASTNode.VAL, t[2], t[4])


def p_valOrFun_fun(t):
    '''valOrFun : FUN frhs
                | FUN frhs SEMI'''
    # TODO: overlap with `fdecl`
    t[0] = (ASTNode.FUNDECL, t[2])


def p_expression_case(t):
    'expression : CASE expression OF caserhs'
    t[0] = (ASTNode.CASE, t[2], t[4])


def p_caserhs(t):
    '''caserhs : caserhs PIPE expression TO expression
               | expression TO expression'''
    if len(t) == 4:
        t[0] = [(ASTNode.CASEEXP, t[1], t[3])]
    else:
        assert len(t) == 6
        t[0] = t[1] + [(ASTNode.CASEEXP, t[3], t[5])]


def p_expression_unit(t):
    '''item : LPAREN RPAREN'''
    t[0] = (ASTNode.TUPLE, None, t[1], t[2])


def p_expression_singleton(t):
    '''item : LPAREN expression RPAREN'''
    t[0] = t[2]  # Losing formatting here.


def p_expression_is_a_tuple(t):
    '''item : tuple'''
    t[0] = t[1]

def p_expression_tuple(t):
    '''tuple : LPAREN expression_list RPAREN
             | LCURL expression_list RCURL'''
    # t[0] = "({0})".format(t[2])
    # We're generalising it a bit and carry the type of parens around
    t[0] = (ASTNode.TUPLE, t[2], t[1], t[3])

# # Bool comparison
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
                  | expression SHAT expression
                  | expression HAT expression'''

    t[0] = (ASTNode.BINEXP, t[1], t[2], t[3])  # infix as before!


def p_expression_tilde(t):
    'expression : TILDE expression'
    # t[0] = "{0}".format(-t[2])
    # t[0] = "{0} {1}".format(t[1], t[2])
    t[0] = (ASTNode.TILDE, t[1], t[2])

def p_expression_ref(t):
    'expression : REF expression'
    # t[0] = t[2]
    # t[0] = "{0} {1}".format(t[1], t[2])
    t[0] = (ASTNode.REF, t[2])


def p_expression_typed(t):
    'expression : expression COLON names'
    t[0] = (ASTNode.TYPED, t[1], t[3])


def p_names(t):
    '''names : names NAME
             | NAME'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        assert len(t) == 3
        t[0] = t[1] + [t[2]]


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
    '''item : NAME
          | item DOT NAME'''
    if len(t) == 2:
        t[0] = ASTNode.ID, str(t[1])
    else:
        assert len(t) == 4
        assert t[1][0] == ASTNode.ID  # otherwise not valid SML
        i = t[1][1]  # extract actual string
        t[0] = ASTNode.ID, str(i) + "." + str(t[3])


def p_item_dots(t):
    'item : DOTS'
    t[0] = ASTNode.ID, str(t[1])


def p_error(t):
    # print("Syntax error at '%s'" % t.value)
    print("Syntax error at '{0}', returning {1}".format(t.value, t))
    # t.error = 1
    raise SyntaxError


# Build the parser
tmpdirname = "/tmp/"
annot_parser = yacc.yacc(start='expression', debugfile=tmpdirname + 'parser.out', write_tables=True)
cond_parser = yacc.yacc(start='guard', debug=tmpdirname + 'guardparser.out', write_tables=False)
fdecls_parser = yacc.yacc(start='fdecls', debug=tmpdirname + 'fdeclsparser.out', write_tables=False)


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


# Declarations in <ml>-tags:
def parse_fdecls(data, debug=0):
    # TODO: refactor all 3 parsers.
    fdecls_parser.error = 0
    try:
        p = fdecls_parser.parse(data, debug=debug)
        if fdecls_parser.error:
            return data
        return p
    except:
        print("Exception: {0}".format(data))
        raise
