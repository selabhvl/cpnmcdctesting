import pytest

import re
import sys
import xml.etree.ElementTree as ET

from CPNParser.cpnexprparse import parse_annot, parse_cond, parse_fdecls, ASTNode
from CPNParser.cpnexprtransf import traverse, traverse_decls, translate_guard
from CPNParser.cpnxml import extract_elements_with_conditions, extract_elements_with_annotations, find_element_by_expr_name, get_cond, set_cond, get_annot, set_annot


cpn_files = ["cpn_models/cpnabs/cpnabs.cpn", "cpn_models/discspcpn/discspcpn.cpn", "cpn_models/mqtt/mqtt.cpn", "cpn_models/paxos/paxos.cpn"]
csv_cond_files = ["cpn_models/cpnabs/cpnabs_trans.csv", "cpn_models/discspcpn/discspcpn_trans.cpn", "cpn_models/mqtt/mqtt_trans.cpn", "cpn_models/paxos/paxos_trans.cpn"]
csv_annot_files = ["cpn_models/cpnabs/cpnabs_arcs.csv", "cpn_models/discspcpn/discspcpn_arcs.cpn", "cpn_models/mqtt/mqtt_arcs.cpn", "cpn_models/paxos/paxos_arcs.cpn"]

# error_cpnabs = ["p9=hd pl9 andalso (if (mem pl27 p9) then p24=p9 else not (p24=p9))"]
error_cpnabs = ["p9=hd pl9"]
error_mqtt = ['1`(id,tag)++1`(id,cval)']
error_paxos = ["if (not b) andalso PrepareQFCond(cid,crnd',preparereplies') then 1`PrepareQFProm(cid,crnd',preparereplies') else empty"]
error_discspcpn = ['1`(id,tag)++1`(id,cval)']

# def add_file_to_load():
#     # type: () -> list
#     # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
#     local_dirs = [x[0] for x in os.walk(self.this_dir)]
#     oraclestl_filenames = []
#     for local_dir in local_dirs:
#         oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
#     return oraclestl_filenames
#
#
# def add_file_to_load_from_folder( folder):
#     # type: (str) -> list
#     # test_dir = self.this_dir + folder
#     test_dir = folder
#     files_path = os.listdir(test_dir)
#     test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
#
#     assert all(os.path.isfile(test) for test in test_txt)
#
#     return test_txt
#
# @pytest.mark.parametrize("original_expected_annot", zip(cpn_files, csv_annot_files))
# def test_arc_transformation(original_expected_annot):
#     original, expected = original_expected_annot
#
#     transformation = [parse(t) for t in original]
#     for i, trans in enumerate(transformation):
#         if trans not in expected:
#             pytest.xfail('{} > {}'.format(original[i], trans))
#
# @pytest.mark.parametrize("original_expected_guard_cond", zip(cpn_files, csv_cond_files))
# def test_transition_transformation(original_expected_guard_cond):
#     original, expected = original_expected_guard_cond
#
#     transformation = [parse_guard(t) for t in original]
#     for i, trans in enumerate(transformation):
#         if trans not in expected:
#             pytest.xfail('{} > {}'.format(original[i], trans))


def test_dec1():
    e = parse_annot("hd foo = bar")
    print(e)
    assert e[0] == ASTNode.BINCOND  # check precedence
    assert e[1][0] == ASTNode.CALL
    et = traverse(e, dec="1")
    print(et)
    assert re.match(r'^AP.*', et) is not None


def test_funcs():
    e = parse_annot("f foo bar")
    assert e[0] == ASTNode.CALL, e  # check precedence
    # No longer true with partial application
    # assert len(e[2]) == 2, e
    et = traverse(e, dec="1")
    assert re.match(r'^AP.*', et) is not None, (e, et)


def test_func():
    e = parse_annot("f()")
    assert e[0] == ASTNode.CALL, e
    assert e[1][0] == ASTNode.ID
    assert e[1][1] == "f"
    assert e[2][0] == ASTNode.TUPLE
    assert e[2][1] == None


def test_fun_decl1a():
    e = parse_fdecls("fun f () = 42;")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e
    assert e[0][1][0][0] == ASTNode.FUN, e


def test_fun_decl1b():
    e = parse_fdecls("fun f () [] = 42;")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e
    assert e[0][1][0][0] == ASTNode.FUN, e


def test_fun_decl2():
    e = parse_fdecls("fun f () = timeout := 42;")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e[0]
    assert e[0][1][0][3][0] == ASTNode.ASSIGN, e[0][2]
    et = traverse_decls(e)
    print(et)


def test_fun_decl3():
    e = parse_fdecls("fun f true = 42 | f false = 7;")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e[0]
    et = traverse_decls(e)
    print(et)


def test_fun_decl4():
    e = parse_fdecls("fun cLR msgs = (List.foldr (fn ((c,omsgs),ln) => ln + (List.length omsgs)) 0 msgs) <= (!boutmsgsbound);")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e[0]
    et = traverse_decls(e)
    print(et)


def test_silly():
    s = "findHighest (acceptreplies)"
    e = parse_annot(s)
    # Okay, so looks like the fun_decl5 is actually suffering from a S/R conflict?!


def test_fun_decl5():
    # e = parse_fdecls("fun AcceptQFLearn (cid,acceptreplies) = let val (crnd,vval) = findHighest (acceptreplies) in rhs end;")
    e = parse_annot("let val x = f x in rhs end")
    assert len(e) == 1
    assert e[0][0] == ASTNode.FUNDECL, e[0]
    et = traverse_decls(e)
    print(et)


def test_mqtt_ml1():
    s = "fun iSubscribe () = List.map (fn qos => QoS(qos)) (!allowSubscribe);"
    e = parse_fdecls(s)
    print(e)
    assert e[0][0] == ASTNode.FUNDECL
    assert e[0][1][0][0] == ASTNode.FUN
    et = traverse_decls(e)
    print(et)
    assert len(e) == len(et)


def test_mqtt_ml2():
    s = "val cpnmcdclibpath =  '../../../';"
    e = parse_fdecls(s)
    print(e)
    et = traverse_decls(e)
    print(et)
    assert len(e) == len(et)


def test_ite1_guard1():
    e = parse_cond("if hd foo = bar then true else false")
    print(e)
    assert e[0] == ASTNode.GUARD
    assert e[2][0] == ASTNode.ITE
    et = traverse(e)
    print(et)
    assert re.match(r'EXPR.*ITE\(.*\, .*\, .*\)', et) is not None, et


def test_ite1_guard2():
    e = parse_cond("[if hd foo = bar then true else false]")
    print(e)
    et = traverse(e)
    print(et)
    assert re.match(r'\[EXPR\(.*\, ITE\(.*\, .*\, .*\)\)\]', et) is not None

def test_exp1():
    e = parse_annot("hd foo = bar")
    print(e)
    et = traverse(e, dec="1")
    print(et)
    assert re.match(r'AP\(.*\)',et) is not None, et

def test_exp2():
    e = parse_annot("if hd fopl1=((ob14,u10,t9,pl11,cl11),0) then ((ob14,u10,t9,pl11,cl11),p5+1)::tl fopl1 else fopl1")
    print(e)
    et = traverse(e)
    print(et)
    assert re.match(r'if EXPR.*',et) is not None

def test_exp3b():
    e = parse_annot("if bexp then x::tl fopl1 else y")
    print(e)
    et = traverse(e)
    print(et)

def test_exp3bguard():
    e = parse_cond("if bexp then x::tl fopl1 else y")
    print(e)
    et = traverse(e)
    print(et)

def test_exp3cguard():
    e = parse_cond("if bexp then x::fopl1 else y")
    print(e)
    et = traverse(e)
    print(et)

def test_exp3dguard():
    e = parse_cond("if bexp then tl fopl1 else y")
    print(e)
    et = traverse(e)
    print(et)

def test_exp3dcond():
    e = parse_annot("if bexp then tl fopl1 else y")
    print(e)
    et = traverse(e)
    print(et)


def test_exp_not1():
    e = parse_annot("not b1")
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.ID
    assert e[1][1] == "not"
    assert e[2][0] == ASTNode.ID, e[2][0]
    assert e[2][1] == "b1"
    print(e)
    et = traverse(e)
    print(et)
    assert re.match(r'not.*b1.*', et) is not None, (e, et)


def test_exp_not2():
    e = parse_annot("(not b1)")
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.ID
    assert e[1][1] == "not"
    et = traverse(e)
    print(et)
    assert re.match(r'not.*b1.*', et) is not None, (e, et)


def test_exp_ref():
    e = parse_annot("! b1")
    assert e[0] == ASTNode.REF
    assert e[1][0] == ASTNode.ID
    assert e[1][1] == "b1"
    print(e)
    et = traverse(e)
    print(et)
    # assert re.match(r'not.*b1.*', et) is not None, (e, et)


def test_guard_not1():
    e = parse_cond("[not b1]")
    print(e)
    et = traverse(e)
    print(et)
    # [EXPR("id1", AP("1", not (b1)))]
    assert re.match(r'\[EXPR\(.*, AP\(.*, not b1\)\)\]', et) is not None, (e, et)

    
def test_exp4():
    s = "1`(id,tag)++1`(id,cval)"
    e = parse_annot(s)
    et = traverse(e)
    print(et)
    # TODO: ick, find a better solution!
    assert et.replace(" ","") == s

def test_arcannot():
    s = "((ob14,u10,t9,pl11,cl11),((ob25,u22,t19,ins pl22 (p12+1),ins cl21 c6),p12+1))::pfopl"
    e = parse_annot(s)
    et = traverse(e)
    print(et)


def test_arc_assign1():
    s = "x = 42"
    e = parse_annot(s)
    assert e[0] == ASTNode.BINCOND
    et = traverse(e)
    print(et)


@pytest.mark.parametrize("expr", error_cpnabs)
def test_cpnabs(expr):
    e = parse_cond(expr)
    # assert e[0] is ASTNode.BINCOND  # `andalso`
    print(e)
    et = traverse(e)
    print(et)
    assert re.match(r'EXPR.*', et) is not None, (e, et)

# @pytest.mark.parametrize("error_mqtt", error_mqtt)
# def test_mqtt(error_mqtt):
#     for expr in error_mqtt:
#         e = parse_cond(expr)
#         print(e)
#         et = traverse(e)
#         print(et)
#         assert et.replace(" ", "") == s


def test_paxos_ok():
    s = "if true then true else empty"
    e = parse_cond(s)
    print(e)
    et = traverse(e)
    print(et)

def test_paxos_err1():
    s = "if (not b) then true else empty"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_constructor1():
    s = "Foo"
    e = parse_annot(s)
    assert e[0] == ASTNode.ID


def test_constructor2():
    s = "Foo 42"
    e = parse_annot(s)
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.ID


def test_constructor3():
    s = "Foo(42)"
    e = parse_annot(s)
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.ID


def test_cons1():
    s = "(42::x)"
    e = parse_annot(s)
    assert e[0] == ASTNode.BINEXP
    assert e[1][0] == ASTNode.ID
    assert e[3][0] == ASTNode.ID


def test_call_exp1():
    s = "f x (y+1)"
    e = parse_annot(s)
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.CALL
    assert e[1][1][1] == "f"
    assert e[2][0] == ASTNode.BINEXP


def test_constructor4():
    s1 = "Foo(42)"
    s2 = "Foo 42"
    e1 = parse_annot(s1)
    e2 = parse_annot(s2)
    assert e1 == e2


def test_call_tuples1():
    s = "rm (x,p20) x"
    e = parse_annot(s)
    assert e[0] == ASTNode.CALL
    assert e[1][0] == ASTNode.CALL
    assert e[1][2][0] == ASTNode.TUPLE, e[2][0]


def test_paxos_err2():
    s = "PrepareQFCond(cid,crnd',preparereplies')"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_paxos_err3():
    s = "if true then 1`PrepareQFProm(cid,crnd',preparereplies') else empty"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)


def test_paxos_err4():
    s = "if PrepareQFCond(cid,crnd',preparereplies') then true else empty"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)


def test_guards2():
    s = "[a = b, c <= 42]"
    e = parse_cond(s)
    print(e)
    et = traverse(e)
    print(et)
    assert re.match(r"\[EXPR\(\"id.*\", AND\(AP\(\"1\", a=b\), AP\(\"2\", c<=42\)\)\)\]", et) is not None


def test_guards3():
    s = "[a = b, c <= 42, ((f 42) - 3) >= 42]"
    e = parse_cond(s)
    print(e)
    et = traverse(e)
    print(et)


def test_let1():
    s = "let val x = 42 in f x end"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)


def test_let2():
    s = "let val x = 42; in f x end"
    e = parse_annot(s)


def test_case1():
    s = "case x of 42 => true | _ => false"
    e = parse_annot(s)


def test_fn_decls1():
    # s = "List.map (fn c => (c,  {topics=[],state=case (!configstate) of cyclic => DISC | _ => READY, pid = 0, roles = getRoles(c)})) (Client.all())"
    s = " fn x => A | _ => B"
    e = parse_annot(s)


def test_fn_decls2():
    s = "List.map (fn c => (c,  {topics=[],state=case (!configstate) of cyclic => DISC | _ => READY, pid = 0, roles = getRoles(c)})) (Client.all())"
    e = parse_annot(s)


def test_typed1():
    s = "42 : int"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)


def test_guards_faustin():
    s = "[the_system_mode=preparing_strong_coffee,(time() - the_request_timer) <= 50 andalso (time() - the_request_timer) >= 30, not(String.isSuffix \"REQ005\" trace) ]"
    e = parse_cond(s)
    print(e)
    et = traverse(e)
    print(et)


@pytest.mark.parametrize("expr", error_paxos)
def test_paxos(expr):
    e = parse_annot(expr)
    print(e)
    et = traverse(e)
    print(et)
    # assert re.match("if EXPR.*", e) is not None, (e, et)

# @pytest.mark.parametrize("error_discspcpn", error_discspcpn)
# def test_discspcpn(error_discspcpn):
#     for expr in error_discspcpn:
#         e = parse_cond(expr)
#         print(e)
#         et = traverse(e)
#         print(et)
#         assert et.replace(" ", "") == s

@pytest.mark.parametrize("in_filename",
                         ["./tests/cpn_models/cpnabs/cpnabs.cpn"])
def test_arc_model(in_filename):
    xml_tree = ET.parse(in_filename)
    arc_errors = []
    arcs = extract_elements_with_annotations(xml_tree)
    for a in arcs:
        expr = get_annot(a)
        if expr is not None:
            inst_expr = ""
            try:
                trimmed_expr = expr.replace("\n", " ")
                # print(trimmed_expr)
                ast = parse_annot(trimmed_expr)
                # print(ast)
                inst_expr = traverse(ast)
                # print(inst_expr)
            except:
                arc_errors.append([trimmed_expr, ast, inst_expr])
                continue

    print("ERRORS")
    for [trimmed_expr, ast, inst_expr] in arc_errors:
        print(trimmed_expr)
        print(ast)
        print(inst_expr)
        print("\n")

    assert len(arc_errors) == 0

@pytest.mark.parametrize("in_filename",
                         ["./tests/cpn_models/cpnabs/cpnabs.cpn"])
def test_trans_model(in_filename):
    xml_tree = ET.parse(in_filename)
    transition_errors = []
    transitions = extract_elements_with_conditions(xml_tree)
    for t in transitions:
        expr = get_cond(t)
        if expr is not None:
            inst_expr = ""
            try:
                trimmed_expr = expr.replace("\n", " ")
                # print(trimmed_expr)
                ast = parse_cond(trimmed_expr)
                # print(ast)
                inst_expr = traverse(ast)
                # print(inst_expr)
                # print("\n")
                # assert re.match(r'^EXPR', inst_expr) is not None
                # inst_expr = EXPR(....) | [EXPR(....)]
                assert re.match(r'(\[)*EXPR', inst_expr) is not None
            except:
                transition_errors.append([trimmed_expr, ast, inst_expr])
                continue

    print("ERRORS")
    for [trimmed_expr, ast, inst_expr] in transition_errors:
        print(trimmed_expr)
        print(ast)
        print(inst_expr)
        print("\n")

    assert len(transition_errors) == 0

def test_cpnabs_arc1():
    s = "if b2=true then " \
        "((ob26,u23,t20,pl23,cl22),p12+1)::ins (rm ((ob25,u22,t19,pl22,cl21),p20) (tl fopl2)) ((ob25,u22,t19, ins pl22 (p12+1),ins cl21 c6),p20) " \
        " else ins (rm ((ob25,u22,t19,pl22,cl21),p20) fopl2) ((ob25,u22,t19, ins pl22 (p12+1),ins cl21 c6),p20)"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_cpnabs_arc2():
    s = "if (mem obpl (ob11,p9)) then 1`p9 else empty"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_cpnabs_arc3():
    s = "if (mem pl27 p9 andalso i4>1) " \
        "then ((ob11,ins (rm p9 pl27) (hd (tl pl9)), ins (rm (p9,i4) pll2) (hd (tl pl9),i4-1))) " \
        "else (if  (mem pl27 p9 andalso i4<=1) then (ob11,rm p9 pl27,rm (p9,i4) pll2) else (ob11,pl27,pll2))"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_cpnabs_arc4():
    s = "rm ((ob24,u21,t18,pl21,cl20),p19) fopl"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_cpnabs_arc5():
    s = "if mem pl25 (hd pl19) then (ob3,ins (rm (hd pl19) pl25) (p17+1),ins (rm (p22,i2) pll) (p17+1,i2+1))  else (ob3,(p17+1)::pl25,(p17+1,1)::pll)"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)


def test_cpnabs_arc6():
    s = "(ob1+1,[],[])"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)

def test_cpnabs_arc7():
    s = "[]"
    e = parse_annot(s)
    print(e)
    et = traverse(e)
    print(et)