import cpnlex
import cpnparse

if __name__ == "__main__":

    # (a < 1) orelse (b > 10) andalso not (c > 20)

    while True:
        try:
            s = input('calc > ')  # Use raw_input on Python 2
        except EOFError:
            break
        res = cpnparse.parse(s)
        print(res)
