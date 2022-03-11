from CPNParser.cpnexprparse import parse_cond, parse_annot, ASTNode

# dictionary of atomic propositions
ap = {}


def ap_identifier(dec, op):
    # type: (str, str) -> str
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


# TODO: Move "traverse(in_cond, t)" intro a "cpnexpr_transform.py"/"CPNExpr_instrument.py"?
def traverse_cond(t, dec=None):
    if t[0] == ASTNode.ID:
        return None
    elif t[0] == ASTNode.EXPR:
        return None
    elif t[0] == ASTNode.LIST:
        return None
    elif t[0] == ASTNode.TILDE:
        return None
    elif t[0] == ASTNode.NOT:
        return None
    elif t[0] == ASTNode.TUPLE:
        return None
    elif t[0] == ASTNode.FN:
        return None
    elif t[0] == ASTNode.GUARDS:
        return None
    elif t[0] == ASTNode.BINEXP:
        return None
    elif t[0] == ASTNode.BINCOND:
        # expression_1 BIN_OP expression_2
        # (ASTNode.BINCOND, expression_1, BIN_OP, expression_2)
        _, expr_1, bin_op, expr_2 = t
        new_bin_op = translate(bin_op)
        op_str = "{0} {1} {2}".format(traverse_cond(expr_1), new_bin_op, traverse_cond(expr_2))
        identifier = ap_identifier(dec, op_str)
        return "AP(\"{0}\", {1})".format(identifier, op_str)
    elif t[0] == ASTNode.CALL:
        op_str = "{0} {1}".format(traverse_cond(t[1]), traverse_cond(t[2]))
        identifier = ap_identifier(dec, op_str)
        return "AP(\"{0}\", {1})".format(identifier, op_str)
    elif t[0] == ASTNode.ID:
        return "{0}".format(t[1])
    elif t[0] == ASTNode.ITE:
        # EXPR(... andalso IF foo then bExp else bExp)
        if t[3] is None:
            assert False, "Not supported?!"
        else:
            return "ITE({0}, {1}, {2})".format(traverse_cond(t[2]), traverse_cond(t[3]), traverse_cond(t[4]))

    else:
        assert False, t


def traverse_annot(t, context=None):
    if t[0] == ASTNode.CALL:
        return "{0} {1}".format(traverse_annot(t[1]), traverse_annot(t[2]))
    elif t[0] == ASTNode.EXPR:
        return None
    elif t[0] == ASTNode.LIST:
        return None
    elif t[0] == ASTNode.TILDE:
        return None
    elif t[0] == ASTNode.NOT:
        return None
    elif t[0] == ASTNode.TUPLE:
        return None
    elif t[0] == ASTNode.FN:
        return None
    elif t[0] == ASTNode.BINEXP:
        return None
    elif t[0] == ASTNode.ID:
        return t[1]
    elif t[0] == ASTNode.ITE:
        # IF expression_1 THEN expression_2 ELSE expression_3
        # (ASTNode.ITE, identifier, expression_1, expression_2, expression_3)
        _, identifier, expr_1, expr_2, expr_3 = t
        if expr_3 is None:
            return "if EXPR(\"{0}\", {1}) then {2}".format(identifier, traverse_annot(expr_1), traverse_annot(expr_2))
        else:
            return "if EXPR(\"{0}\", {1}) then {2} else {3}".format(identifier, traverse_annot(expr_1), traverse_annot(expr_2), traverse_annot(expr_3))
    elif t[0] == ASTNode.GUARDS:
        return "[{0}]".format(traverse_annot(t[1]))
    else:
        assert False, t