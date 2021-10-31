# (* boolean conditions *)
#
# datatype condition = AND of condition * condition
# 		   | OR of condition * condition
# 			 | ANDlr of condition * condition
# 			 | ORlr of condition * condition
# 		   | NOT of condition
# 			 | ITE of condition * condition * condition
# 			 | ITElr of condition * condition * condition
# 		   | AP of string * bool;
#
# (* TODO: can be implementented more efficient
#    - using accumulation and
#    - tail recursion
#
# *)
#
# fun countQs (AP(_,_)) = [("?",NONE)]
#   | countQs (AND(l,r)) = countQs l^^countQs r
# 	| countQs (ANDlr(l,r)) = countQs l^^countQs r
# 	| countQs (OR(l,r)) = countQs l^^countQs r
# 	| countQs (ORlr(l,r)) = countQs l^^countQs r
# 	| countQs (NOT(x)) = countQs x
# 	| countQs (ITE(c,l,r)) = countQs c ^^ countQs l ^^ countQs r
#   | countQs (ITElr(c,l,r)) = countQs c ^^ countQs l ^^ countQs r
# 	;
#
# fun eval (AP (cond,v)) = ([(cond, SOME v)],v)
#   | eval (OR (a,b)) =
#     let
# 	val (ares,a') = eval a;
# 	val (bres,b') = eval b;
#     in
# 	(ares^^bres,a' orelse b')
#     end
# 	| eval (ORlr (a,b)) =
# 	    let
# 		val (ares,a') = eval a;
# 	    in
# 			if a' then (ares^^countQs b, a' (* true *) )
# 			      else let val (bres,b') = eval b; in
# 		             (ares^^bres,(* a' orelse *) b') end
# 	    end
#   | eval (AND (a,b)) =
#     let
# 	val (ares,a') = eval a;
# 	val (bres,b') = eval b;
#     in
# 	(ares^^bres,a' andalso b')
#     end
# 	| eval (ANDlr (a,b)) =
# 	    let
# 		val (ares,a') = eval a
# 	    in if a' then let val (bres,b') = eval b; in
# 		                (ares^^bres,(* a' andalso *) b') end
# 		           else (ares^^countQs b, a' (* false *))
# 	    end
#   | eval (NOT a) =
#     let
# 	val (ares,a') = eval a;
#     in
# 	(ares,not a')
# 	  end
#  | eval (ITE (c,l,r)) =
#  	 let
# 			val (cres,c') = eval c;
# 			val (lres,l') = eval l;
# 			val (rres,r') = eval r;
# 	 in (cres^^lres^^rres, (c' andalso l') orelse r')
# 	 end
# 	| eval (ITElr (c,l,r)) =
#   	let
# 	 		val (cres,c') = eval c;
# 		in if c' then let
# 	 		    val (lres,l') = eval l;
# 			    in (cres^^lres^^countQs r, l') end
# 			 else let
# 	 		    val (rres,r') = eval r;
# 	 	      in (cres^^countQs l^^rres, r') end
#     end;
#
#
# fun resToString res =
#   String.concat (
#   List.map
#       (fn (cond,v) => (case v of NONE => "?"
# 				| SOME b => if b then "1" else "0"))
#       res);
#
# fun EXPR (name,expr) =
#   let
#       val (res,expr') = eval expr;
#       val _ = Logging.log (name^":"^resToString res^":"^(if expr' then "1" else "0"));
#   in
#       expr'
#   end

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
    'LPAREN', 'RPAREN'
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


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Parsing rules
precedence = (
    ('nonassoc', 'LESS', 'GREATER'),  # Nonassociative operators
    ('nonassoc', 'LEQ', 'GEQ'),       # Nonassociative operators
    ('nonassoc', 'EQUALS', 'NEQ'),    # Nonassociative operators
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

# dictionary of atomic propositions
ap = {}


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    names[t[1]] = t[3]


def p_statement_expr(t):
    'statement : expression'
    t[0] = t[1]


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
        if op not in ap:
            ap[op] = len(ap)
        identifier = ap[op]
        t[0] = "AP({0}, {1})".format(identifier, op)
    elif t[2] == 'orelse':
        t[0] = "OR({0}, {1})".format(t[1], t[3])
    elif t[2] == 'andalso':
        t[0] = "AND({0}, {1})".format(t[1], t[3])


# expression
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
'''

    op = "{0} {1} {2}".format(t[1], t[2], t[3])
    if op not in ap:
        ap[op] = len(ap)
    identifier = ap[op]
    t[0] = "AP({0}, {1})".format(identifier, op)


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


# Build the parser
parser = yacc.yacc()

# Example:
# the_pressure_mode := 0
# the_water_pressure := 1
# permitted := true
# (the_pressure_mode = permitted)  andalso   not (the_water_pressure  < 9)  andalso  (the_water_pressure  < 9)
# not (the_water_pressure < 9)  andalso  (the_water_pressure  < 9)
# not a < b
while True:
    try:
        s = input('calc > ')  # Use raw_input on Python 2
    except EOFError:
        break
    res = parser.parse(s)
    print(res)
