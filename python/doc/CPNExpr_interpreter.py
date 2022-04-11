import CPNParser.cpnexprlex
from CPNParser.cpnexprparse import parse_cond

if __name__ == "__main__":

    # (a < 1) orelse (b > 10) andalso not (c > 20)

    while True:
        try:
            s = input('calc > ')  # Use raw_input on Python 2
        except EOFError:
            break
        res = parse_cond(s)
        print(res)
