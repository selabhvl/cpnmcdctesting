from CPNParser.cpnexprparse import parse_cond, parse_annot, ASTNode, ex_identifier

# dictionary of atomic propositions
ap = {}


def ap_identifier(dec, op):
    # type: (str, str) -> str
    assert dec is not None
    if dec not in ap:
        ap[dec] = {}
    if op not in dec:
        ap[dec][op] = len(ap[dec]) + 1
    identifier = ap[dec][op]
    return identifier


def translate(bin_op):
    # type: (str) -> str
    if bin_op == "andalso":
        return "AND"
    elif bin_op == "orelse":
        return "OR"
    else:
        return bin_op


# def binop_ap(dec, expr_1, bin_op, expr_2):
#     # type: (str, str, str, str) -> (str, str)
#     new_bin_op = translate(bin_op)
#     op_str = "{0} {1} {2}".format(traverse_cond(expr_1), new_bin_op, traverse_cond(expr_2))
#     identifier = ap_identifier(dec, op_str)
#     return identifier, op_str

def translate_ite(t, dec):
    # decision = id(expression_1)
    # IF expression_1 THEN expression_2 ELSE expression_3
    # (ASTNode.ITE, decision, expression_1, expression_2, expression_3)
    _, if_dec, expr_1, expr_2, expr_3 = t
    if dec is not None:
        if expr_3 is not None:
            # EXPR(... andalso IF foo then bExp else bExp)
            return "ITE({0}, {1}, {2})".format(traverse(expr_1, dec),
                                               traverse(expr_2, dec),
                                               traverse(expr_3, dec))
        else:
            assert False, "Not supported?!"
    else:
        if expr_3 is None:
            return "if EXPR(\"{0}\", {1}) then {2}".format(if_dec,
                                                           traverse(expr_1, if_dec),
                                                           traverse(expr_2, dec=None))
        else:
            return "if EXPR(\"{0}\", {1}) then {2} else {3}".format(if_dec,
                                                                    traverse(expr_1, if_dec),
                                                                    traverse(expr_2, dec=None),
                                                                    traverse(expr_3, dec=None))


def translate_call(t, dec):
    # expression expression %prec FCALL
    # (ASTNode.CALL, expression, expression)
    _, expr_1, exprs = t
    # TODO: we loose input format here and print everything with nested parens.
    #str_expr_list = " ".join("({0})".format(traverse(expr, dec)) for expr in exprs)
    str_expr_list = traverse(exprs, dec)
    if dec is not None:
        identifier = ap_identifier(dec, str_expr_list)
        return "AP(\"{0}\", {1} {2})".format(identifier, traverse(expr_1), str_expr_list)
    else:
        return "{0} {1}".format(traverse(expr_1), str_expr_list)


def translate_single_guard(t, dec):
    # expression
    # (ASTNode.GUARD, decision, expression)
    assert t[0] == ASTNode.GUARD
    _, guard_dec, expr = t
    str_expr = traverse(expr, guard_dec)
    return "EXPR(\"{0}\", {1})".format(guard_dec, str_expr)
    # return "[{0}]".format(traverse(expr_list, dec))


def translate_guard(t, dec):
    # decision = id(expression_list)
    # LBRACK expression_list RBRACK
    # (ASTNode.GUARDS, decision, expression_list)
    assert t[0] == ASTNode.GUARDS
    _, guard_dec, expr_list = t
    str_expr_list = ",".join(traverse(expr, guard_dec) for expr in expr_list)
    return "[EXPR(\"{0}\", {1})]".format(guard_dec, str_expr_list)
    # return "[{0}]".format(traverse(expr_list, dec))


def translate_nil(t, dec):
    return "[]"


def translate_list(t, dec):
    # LBRACK expression_list RBRACK
    # (ASTNode.LIST, expression_list)
    _, expr_list = t
    str_expr_list = ",".join(traverse(expr, dec) for expr in expr_list)
    return "{0}".format(str_expr_list)


def translate_fn(t, dec):
    # FN NAME TO expression
    # (ASTNode.FN, name, expression)
    _, name, expr = t
    return "fn {0} => {1}".format(name, traverse(expr, dec=None))


def translate_tuple(t, dec):
    # LPAREN expression_list RPAREN
    # (ASTNode.TUPLE, expression_list)
    # Warning! expression_list is None when empty list, i.e., LPAREN RPAREN
    _, expr_list = t
    str_expr_list = ",".join(traverse(expr, dec) for expr in expr_list) if expr_list is not None else ""
    return "(" + str_expr_list + ")"


def translate_ref(t, dec):
    # REF expression
    # (ASTNode.REF, expression)
    _, expr = t
    return "!{0}".format(traverse(expr, dec=None))


def translate_binexp(t, dec):
    # expression_1 BIN_OP expression_2
    # (ASTNode.BINEXP, expression_1, BIN_OP, expression_2)
    _, expr_1, bin_op, expr_2 = t
    if dec is None:
        return "{0}{1}{2}".format(traverse(expr_1, dec=None),
                                  bin_op,
                                  traverse(expr_2, dec=None))
    else:
        op_str = "{0}{1}{2}".format(traverse(expr_1, dec=None),
                                    bin_op,
                                    traverse(expr_2, dec=None))
        identifier = ap_identifier(dec, op_str)
        return "AP(\"{0}\", {1})".format(identifier, op_str)


def translate_bincond(t, dec):
    # expression_1 BIN_OP expression_2
    # (ASTNode.BINCOND, expression_1, BIN_OP, expression_2)
    _, expr_1, bin_op, expr_2 = t

    # The following code should not be necessary.
    # If the binary condition is on top of the expression, then we are in a guard
    # and guards have associated the 'dec' identifier.
    # if dec is None:
    #     # Binary condicion is on the top, so we are opening a new decision
    #     id_list = id(t)
    #     dec = ex_identifier(str(id_list))

    # identifier, op_str = binop_ap(dec, expr_1, bin_op, expr_2)
    # return "AP(\"{0}\", {1})".format(identifier, op_str)
    if dec is None:
        return "{0}{1}{2}".format(traverse(expr_1, dec),
                                    bin_op,
                                    traverse(expr_2, dec))
    else:
        new_bin_op = translate(bin_op)
        if (new_bin_op == "AND") or (new_bin_op == "OR"):
            return "{0}({1}, {2})".format(new_bin_op,
                                          traverse(expr_1, dec),
                                          traverse(expr_2, dec))
        else:
            op_str = "{0}{1}{2}".format(traverse(expr_1, dec=None),
                                        new_bin_op,
                                        traverse(expr_2, dec=None))
            identifier = ap_identifier(dec, op_str)
            return "AP(\"{0}\", {1})".format(identifier, op_str)


def translate_tilde(t, dec):
    # TILDE expression
    # (ASTNode.TILDE, tilde, expression)
    _, tilde, expr = t
    return "{0}{1}".format(tilde,
                           traverse(expr, dec))

def translate_id(t, dec):
    return "{0}".format(t[1])


def translate_constructor(t, dec):
    # NAME LPAREN expression_list RPAREN
    # (ASTNode.CONSTRUCTOR, (ASTNode.ID, name), expression_list)
    _, (_, name), expr_list = t
    str_expr_list = ",".join(traverse(expr, dec) for expr in expr_list) if expr_list is not None else ""
    return "{0}({1})".format(name, str_expr_list)

def translate_hash(t, dec):
    # CHAR NAME expression
    # | CHAR NUMBER expression
    # (ASTNode.HASH, t[2], t[3])
    _, name, expr = t
    return "# {0} {1}".format(name, traverse(expr, dec=None))


def translate_fun(t, dec):
    # FUN NAME expressions EQUALS expression SEMI
    # (ASTNode.FUN, t[2], t[3], t[5])
    assert t[0] == ASTNode.FUN
    _, name, expr_list, expr = t
    str_expr_list = ",".join(traverse(expr, dec=None) for expr in expr_list) if expr_list is not None else ""
    return "fun {0} {1} = {2};".format(name,
                                str_expr_list,
                                traverse(expr, dec=None))


def translate_val(t, dec):
    # VAL NAME EQUALS expression SEMI
    # (ASTNode.VAL, t[2], t[4])
    assert t[0] == ASTNode.VAL
    _, name, expr = t
    return "val {0} = {1};".format(name, traverse(expr, dec=None))


def traverse(t, dec=None):
    if t[0] == ASTNode.ITE:
        return translate_ite(t, dec)
    elif t[0] == ASTNode.CALL:
        return translate_call(t, dec)
    elif t[0] == ASTNode.GUARD:
        # single!
        return translate_single_guard(t, dec)
    elif t[0] == ASTNode.GUARDS:
        # list!
        return translate_guard(t, dec)
    elif t[0] == ASTNode.NIL:
        return translate_nil(t, dec)
    elif t[0] == ASTNode.LIST:
        return translate_list(t, dec)
    elif t[0] == ASTNode.FN:
        translate_fn(t, dec)
    elif t[0] == ASTNode.TUPLE:
        return translate_tuple(t, dec)
    elif t[0] == ASTNode.REF:
        return translate_ref(t, dec)
    elif t[0] == ASTNode.BINEXP:
        return translate_binexp(t, dec)
    elif t[0] == ASTNode.BINCOND:
        return translate_bincond(t, dec)
    elif t[0] == ASTNode.TILDE:
        return translate_tilde(t, dec)
    elif t[0] == ASTNode.ID:
        return translate_id(t, dec)
    elif t[0] == ASTNode.CONSTRUCTOR:
        return translate_constructor(t, dec)
    elif t[0] == ASTNode.HASH:
        return translate_hash(t, dec)
    elif t[0] == ASTNode.FUN:
        assert False, "Unreached."
        return translate_fun(t, dec)
    elif type(t[0]) == str:
        # TODO: What happens when the AST arrives to a terminal node (e.g., expression = NUMBER)?
        return t[0]
    else:
        assert False, t


def traverse_decl(t):
    if t[0] == ASTNode.FUN:
        return translate_fun(t, dec=None)
    elif t[0] == ASTNode.VAL:
        return translate_val(t, dec=None)
    else:
        assert False


def traverse_decls(t):
    return list(map(traverse_decl, t))
