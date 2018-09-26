def digit_sum(digit):
    n1 = int("{0}".format(digit))
    n2 = int("{0}{1}".format(digit,digit))
    n3 = int("{0}{1}{2}".format(digit,digit,digit))
    n4 = int("{0}{1}{2}{3}".format(digit,digit,digit,digit))
    total = n1+n2+n3+n4
    return total
